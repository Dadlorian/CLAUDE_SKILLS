# Trading API Integration Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Order Entry and Management APIs](#order-entry-and-management-apis)
3. [Market Data APIs](#market-data-apis)
4. [FIX Protocol Integration](#fix-protocol-integration)
5. [Low-Latency API Design Patterns](#low-latency-api-design-patterns)
6. [Risk Check Integration](#risk-check-integration)
7. [Position and Account APIs](#position-and-account-apis)
8. [Error Handling and Retry Logic](#error-handling-and-retry-logic)
9. [Rate Limiting Patterns](#rate-limiting-patterns)
10. [Security Considerations](#security-considerations)
11. [Production-Grade Practices](#production-grade-practices)
12. [Provider Examples](#provider-examples)

## Introduction

Trading API integration requires careful consideration of performance, reliability, and regulatory compliance. This guide covers best practices for building robust trading systems that can handle high-frequency operations while maintaining data integrity and security.

### Key Principles
- **Low Latency**: Minimize round-trip time for critical operations
- **Reliability**: Handle network issues and ensure order delivery
- **Risk Management**: Implement pre-trade and post-trade risk checks
- **Audit Trail**: Maintain complete records of all trading activity
- **Compliance**: Adhere to regulatory requirements (MiFID II, Reg NMS, etc.)

## Order Entry and Management APIs

### Order Types and Structures

```typescript
enum OrderType {
  MARKET = 'MARKET',
  LIMIT = 'LIMIT',
  STOP = 'STOP',
  STOP_LIMIT = 'STOP_LIMIT',
  TRAILING_STOP = 'TRAILING_STOP',
  ICEBERG = 'ICEBERG',
  TWAP = 'TWAP',
  VWAP = 'VWAP',
}

enum OrderSide {
  BUY = 'BUY',
  SELL = 'SELL',
}

enum TimeInForce {
  DAY = 'DAY',
  GTC = 'GTC', // Good Till Canceled
  IOC = 'IOC', // Immediate or Cancel
  FOK = 'FOK', // Fill or Kill
  GTD = 'GTD', // Good Till Date
}

enum OrderStatus {
  PENDING = 'PENDING',
  OPEN = 'OPEN',
  PARTIALLY_FILLED = 'PARTIALLY_FILLED',
  FILLED = 'FILLED',
  CANCELED = 'CANCELED',
  REJECTED = 'REJECTED',
  EXPIRED = 'EXPIRED',
}

interface Order {
  orderId: string;
  clientOrderId: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number; // For limit orders
  stopPrice?: number; // For stop orders
  timeInForce: TimeInForce;
  status: OrderStatus;
  filledQuantity: number;
  averagePrice?: number;
  createdAt: Date;
  updatedAt: Date;
  metadata?: Record<string, string>;
}

interface OrderRequest {
  clientOrderId: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  quantity: number;
  price?: number;
  stopPrice?: number;
  timeInForce: TimeInForce;
  metadata?: Record<string, string>;
}
```

### Order Placement

```typescript
class TradingOrderService {
  private readonly apiClient: any;
  private readonly riskManager: RiskManager;

  constructor(apiClient: any, riskManager: RiskManager) {
    this.apiClient = apiClient;
    this.riskManager = riskManager;
  }

  async placeOrder(request: OrderRequest): Promise<Order> {
    // Pre-trade risk checks
    await this.riskManager.validateOrder(request);

    try {
      const response = await this.apiClient.post('/api/v1/orders', {
        clientOrderId: request.clientOrderId,
        symbol: request.symbol,
        side: request.side,
        type: request.type,
        quantity: request.quantity,
        price: request.price,
        stopPrice: request.stopPrice,
        timeInForce: request.timeInForce,
        timestamp: Date.now(),
      });

      const order: Order = {
        orderId: response.data.orderId,
        clientOrderId: request.clientOrderId,
        symbol: request.symbol,
        side: request.side,
        type: request.type,
        quantity: request.quantity,
        price: request.price,
        stopPrice: request.stopPrice,
        timeInForce: request.timeInForce,
        status: OrderStatus.PENDING,
        filledQuantity: 0,
        createdAt: new Date(),
        updatedAt: new Date(),
        metadata: request.metadata,
      };

      // Log order placement
      await this.logOrderActivity('ORDER_PLACED', order);

      return order;
    } catch (error) {
      await this.handleOrderError(error, request);
      throw error;
    }
  }

  async placeBracketOrder(
    entryOrder: OrderRequest,
    takeProfitPrice: number,
    stopLossPrice: number
  ): Promise<{ entry: Order; takeProfit: Order; stopLoss: Order }> {
    // Place entry order
    const entry = await this.placeOrder(entryOrder);

    // Place take profit order
    const takeProfit = await this.placeOrder({
      clientOrderId: `${entry.clientOrderId}_TP`,
      symbol: entry.symbol,
      side: entry.side === OrderSide.BUY ? OrderSide.SELL : OrderSide.BUY,
      type: OrderType.LIMIT,
      quantity: entry.quantity,
      price: takeProfitPrice,
      timeInForce: TimeInForce.GTC,
    });

    // Place stop loss order
    const stopLoss = await this.placeOrder({
      clientOrderId: `${entry.clientOrderId}_SL`,
      symbol: entry.symbol,
      side: entry.side === OrderSide.BUY ? OrderSide.SELL : OrderSide.BUY,
      type: OrderType.STOP,
      quantity: entry.quantity,
      stopPrice: stopLossPrice,
      timeInForce: TimeInForce.GTC,
    });

    return { entry, takeProfit, stopLoss };
  }

  async cancelOrder(orderId: string): Promise<Order> {
    const response = await this.apiClient.delete(`/api/v1/orders/${orderId}`, {
      data: { timestamp: Date.now() },
    });

    const order = this.mapResponseToOrder(response.data);
    await this.logOrderActivity('ORDER_CANCELED', order);

    return order;
  }

  async modifyOrder(
    orderId: string,
    updates: Partial<OrderRequest>
  ): Promise<Order> {
    const response = await this.apiClient.put(`/api/v1/orders/${orderId}`, {
      ...updates,
      timestamp: Date.now(),
    });

    const order = this.mapResponseToOrder(response.data);
    await this.logOrderActivity('ORDER_MODIFIED', order);

    return order;
  }

  async getOrder(orderId: string): Promise<Order> {
    const response = await this.apiClient.get(`/api/v1/orders/${orderId}`);
    return this.mapResponseToOrder(response.data);
  }

  async getOpenOrders(symbol?: string): Promise<Order[]> {
    const params = symbol ? { symbol } : {};
    const response = await this.apiClient.get('/api/v1/orders/open', { params });
    return response.data.map((o: any) => this.mapResponseToOrder(o));
  }

  async getOrderHistory(
    symbol?: string,
    startTime?: Date,
    endTime?: Date
  ): Promise<Order[]> {
    const response = await this.apiClient.get('/api/v1/orders/history', {
      params: {
        symbol,
        startTime: startTime?.getTime(),
        endTime: endTime?.getTime(),
      },
    });
    return response.data.map((o: any) => this.mapResponseToOrder(o));
  }

  private mapResponseToOrder(data: any): Order {
    return {
      orderId: data.orderId,
      clientOrderId: data.clientOrderId,
      symbol: data.symbol,
      side: data.side,
      type: data.type,
      quantity: data.quantity,
      price: data.price,
      stopPrice: data.stopPrice,
      timeInForce: data.timeInForce,
      status: data.status,
      filledQuantity: data.filledQuantity,
      averagePrice: data.averagePrice,
      createdAt: new Date(data.createdAt),
      updatedAt: new Date(data.updatedAt),
      metadata: data.metadata,
    };
  }

  private async logOrderActivity(action: string, order: Order): Promise<void> {
    console.log(`[${action}] Order ${order.orderId}: ${order.symbol} ${order.side} ${order.quantity} @ ${order.price || 'MARKET'}`);
  }

  private async handleOrderError(error: any, request: OrderRequest): Promise<void> {
    console.error('Order placement failed:', {
      clientOrderId: request.clientOrderId,
      symbol: request.symbol,
      error: error.message,
    });
  }
}
```

### Algorithmic Order Execution

```typescript
interface TWAPConfig {
  symbol: string;
  side: OrderSide;
  totalQuantity: number;
  duration: number; // milliseconds
  slices: number;
}

class AlgorithmicOrderExecutor {
  private readonly orderService: TradingOrderService;

  constructor(orderService: TradingOrderService) {
    this.orderService = orderService;
  }

  async executeTWAP(config: TWAPConfig): Promise<Order[]> {
    const orders: Order[] = [];
    const sliceQuantity = config.totalQuantity / config.slices;
    const interval = config.duration / config.slices;

    for (let i = 0; i < config.slices; i++) {
      const order = await this.orderService.placeOrder({
        clientOrderId: `TWAP_${config.symbol}_${Date.now()}_${i}`,
        symbol: config.symbol,
        side: config.side,
        type: OrderType.MARKET,
        quantity: sliceQuantity,
        timeInForce: TimeInForce.IOC,
      });

      orders.push(order);

      if (i < config.slices - 1) {
        await this.sleep(interval);
      }
    }

    return orders;
  }

  async executeVWAP(
    symbol: string,
    side: OrderSide,
    totalQuantity: number,
    volumeProfile: number[]
  ): Promise<Order[]> {
    const orders: Order[] = [];

    for (let i = 0; i < volumeProfile.length; i++) {
      const quantity = totalQuantity * volumeProfile[i];

      const order = await this.orderService.placeOrder({
        clientOrderId: `VWAP_${symbol}_${Date.now()}_${i}`,
        symbol: symbol,
        side: side,
        type: OrderType.MARKET,
        quantity: quantity,
        timeInForce: TimeInForce.IOC,
      });

      orders.push(order);
    }

    return orders;
  }

  async executeIcebergOrder(
    symbol: string,
    side: OrderSide,
    totalQuantity: number,
    displayQuantity: number,
    price: number
  ): Promise<Order[]> {
    const orders: Order[] = [];
    let remainingQuantity = totalQuantity;

    while (remainingQuantity > 0) {
      const quantity = Math.min(displayQuantity, remainingQuantity);

      const order = await this.orderService.placeOrder({
        clientOrderId: `ICEBERG_${symbol}_${Date.now()}`,
        symbol: symbol,
        side: side,
        type: OrderType.LIMIT,
        quantity: quantity,
        price: price,
        timeInForce: TimeInForce.GTC,
      });

      orders.push(order);

      // Wait for fill before placing next slice
      await this.waitForOrderFill(order.orderId);
      remainingQuantity -= quantity;
    }

    return orders;
  }

  private async waitForOrderFill(orderId: string): Promise<void> {
    while (true) {
      const order = await this.orderService.getOrder(orderId);
      if (order.status === OrderStatus.FILLED || order.status === OrderStatus.CANCELED) {
        break;
      }
      await this.sleep(100);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
```

## Market Data APIs

### REST API for Historical Data

```typescript
interface OHLCV {
  timestamp: Date;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface Ticker {
  symbol: string;
  lastPrice: number;
  bidPrice: number;
  askPrice: number;
  bidSize: number;
  askSize: number;
  volume24h: number;
  priceChange24h: number;
  priceChangePercent24h: number;
  timestamp: Date;
}

class MarketDataService {
  private readonly apiClient: any;

  constructor(apiClient: any) {
    this.apiClient = apiClient;
  }

  async getTicker(symbol: string): Promise<Ticker> {
    const response = await this.apiClient.get('/api/v1/ticker', {
      params: { symbol },
    });

    return {
      symbol: response.data.symbol,
      lastPrice: parseFloat(response.data.lastPrice),
      bidPrice: parseFloat(response.data.bidPrice),
      askPrice: parseFloat(response.data.askPrice),
      bidSize: parseFloat(response.data.bidSize),
      askSize: parseFloat(response.data.askSize),
      volume24h: parseFloat(response.data.volume),
      priceChange24h: parseFloat(response.data.priceChange),
      priceChangePercent24h: parseFloat(response.data.priceChangePercent),
      timestamp: new Date(response.data.timestamp),
    };
  }

  async getOHLCV(
    symbol: string,
    interval: string,
    limit?: number,
    startTime?: Date,
    endTime?: Date
  ): Promise<OHLCV[]> {
    const response = await this.apiClient.get('/api/v1/klines', {
      params: {
        symbol,
        interval,
        limit,
        startTime: startTime?.getTime(),
        endTime: endTime?.getTime(),
      },
    });

    return response.data.map((k: any) => ({
      timestamp: new Date(k[0]),
      open: parseFloat(k[1]),
      high: parseFloat(k[2]),
      low: parseFloat(k[3]),
      close: parseFloat(k[4]),
      volume: parseFloat(k[5]),
    }));
  }

  async getOrderBook(symbol: string, depth: number = 20): Promise<OrderBook> {
    const response = await this.apiClient.get('/api/v1/depth', {
      params: { symbol, limit: depth },
    });

    return {
      symbol,
      bids: response.data.bids.map((b: any) => ({
        price: parseFloat(b[0]),
        quantity: parseFloat(b[1]),
      })),
      asks: response.data.asks.map((a: any) => ({
        price: parseFloat(a[0]),
        quantity: parseFloat(a[1]),
      })),
      timestamp: new Date(),
    };
  }

  async getTrades(symbol: string, limit: number = 100): Promise<Trade[]> {
    const response = await this.apiClient.get('/api/v1/trades', {
      params: { symbol, limit },
    });

    return response.data.map((t: any) => ({
      id: t.id,
      symbol: symbol,
      price: parseFloat(t.price),
      quantity: parseFloat(t.qty),
      timestamp: new Date(t.time),
      isBuyerMaker: t.isBuyerMaker,
    }));
  }
}

interface OrderBook {
  symbol: string;
  bids: { price: number; quantity: number }[];
  asks: { price: number; quantity: number }[];
  timestamp: Date;
}

interface Trade {
  id: string;
  symbol: string;
  price: number;
  quantity: number;
  timestamp: Date;
  isBuyerMaker: boolean;
}
```

### WebSocket for Real-Time Data

```typescript
import WebSocket from 'ws';
import { EventEmitter } from 'events';

enum WebSocketMessageType {
  SUBSCRIBE = 'SUBSCRIBE',
  UNSUBSCRIBE = 'UNSUBSCRIBE',
  TICKER = 'ticker',
  TRADE = 'trade',
  ORDERBOOK = 'depthUpdate',
  KLINE = 'kline',
}

class MarketDataWebSocket extends EventEmitter {
  private ws: WebSocket | null = null;
  private readonly url: string;
  private reconnectAttempts: number = 0;
  private readonly maxReconnectAttempts: number = 10;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private subscriptions: Set<string> = new Set();

  constructor(url: string) {
    super();
    this.url = url;
  }

  connect(): void {
    this.ws = new WebSocket(this.url);

    this.ws.on('open', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.resubscribe();
      this.emit('connected');
    });

    this.ws.on('message', (data: string) => {
      this.handleMessage(data);
    });

    this.ws.on('error', (error: Error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    });

    this.ws.on('close', () => {
      console.log('WebSocket disconnected');
      this.stopHeartbeat();
      this.emit('disconnected');
      this.reconnect();
    });

    this.ws.on('ping', () => {
      this.ws?.pong();
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopHeartbeat();
  }

  subscribe(channel: string, symbol: string): void {
    const subscription = `${symbol}@${channel}`;
    this.subscriptions.add(subscription);

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          method: WebSocketMessageType.SUBSCRIBE,
          params: [subscription],
          id: Date.now(),
        })
      );
    }
  }

  unsubscribe(channel: string, symbol: string): void {
    const subscription = `${symbol}@${channel}`;
    this.subscriptions.delete(subscription);

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          method: WebSocketMessageType.UNSUBSCRIBE,
          params: [subscription],
          id: Date.now(),
        })
      );
    }
  }

  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);

      if (message.e === WebSocketMessageType.TICKER) {
        this.emit('ticker', this.parseTicker(message));
      } else if (message.e === WebSocketMessageType.TRADE) {
        this.emit('trade', this.parseTrade(message));
      } else if (message.e === WebSocketMessageType.ORDERBOOK) {
        this.emit('orderbook', this.parseOrderBookUpdate(message));
      } else if (message.e === WebSocketMessageType.KLINE) {
        this.emit('kline', this.parseKline(message));
      }
    } catch (error) {
      console.error('Failed to parse message:', error);
    }
  }

  private parseTicker(data: any): Ticker {
    return {
      symbol: data.s,
      lastPrice: parseFloat(data.c),
      bidPrice: parseFloat(data.b),
      askPrice: parseFloat(data.a),
      bidSize: parseFloat(data.B),
      askSize: parseFloat(data.A),
      volume24h: parseFloat(data.v),
      priceChange24h: parseFloat(data.p),
      priceChangePercent24h: parseFloat(data.P),
      timestamp: new Date(data.E),
    };
  }

  private parseTrade(data: any): Trade {
    return {
      id: data.t.toString(),
      symbol: data.s,
      price: parseFloat(data.p),
      quantity: parseFloat(data.q),
      timestamp: new Date(data.T),
      isBuyerMaker: data.m,
    };
  }

  private parseOrderBookUpdate(data: any): any {
    return {
      symbol: data.s,
      bids: data.b.map((b: any) => ({
        price: parseFloat(b[0]),
        quantity: parseFloat(b[1]),
      })),
      asks: data.a.map((a: any) => ({
        price: parseFloat(a[0]),
        quantity: parseFloat(a[1]),
      })),
      timestamp: new Date(data.E),
    };
  }

  private parseKline(data: any): OHLCV {
    const k = data.k;
    return {
      timestamp: new Date(k.t),
      open: parseFloat(k.o),
      high: parseFloat(k.h),
      low: parseFloat(k.l),
      close: parseFloat(k.c),
      volume: parseFloat(k.v),
    };
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.ping();
      }
    }, 30000); // 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private reconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnect attempts reached');
      this.emit('maxReconnectAttemptsReached');
      return;
    }

    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    console.log(`Reconnecting in ${delay}ms...`);

    setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  private resubscribe(): void {
    for (const subscription of this.subscriptions) {
      const [symbol, channel] = subscription.split('@');
      this.subscribe(channel, symbol);
    }
  }
}

// Usage
const marketDataWs = new MarketDataWebSocket('wss://stream.exchange.com/ws');

marketDataWs.on('ticker', (ticker: Ticker) => {
  console.log(`Ticker: ${ticker.symbol} - ${ticker.lastPrice}`);
});

marketDataWs.on('trade', (trade: Trade) => {
  console.log(`Trade: ${trade.symbol} - ${trade.price} x ${trade.quantity}`);
});

marketDataWs.on('orderbook', (update: any) => {
  console.log(`OrderBook Update: ${update.symbol}`);
});

marketDataWs.connect();
marketDataWs.subscribe('ticker', 'BTCUSD');
marketDataWs.subscribe('trade', 'BTCUSD');
```

## FIX Protocol Integration

### FIX Session Management

```typescript
import { EventEmitter } from 'events';

class FIXSession extends EventEmitter {
  private readonly senderCompID: string;
  private readonly targetCompID: string;
  private messageSequenceNumber: number = 1;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private readonly heartbeatIntervalMs: number = 30000;

  constructor(senderCompID: string, targetCompID: string) {
    super();
    this.senderCompID = senderCompID;
    this.targetCompID = targetCompID;
  }

  createMessage(msgType: string, fields: Record<string, string>): string {
    const timestamp = this.getTimestamp();

    const body = Object.entries({
      ...fields,
      '49': this.senderCompID, // SenderCompID
      '56': this.targetCompID, // TargetCompID
      '34': this.messageSequenceNumber.toString(), // MsgSeqNum
      '52': timestamp, // SendingTime
    })
      .map(([tag, value]) => `${tag}=${value}`)
      .join('|');

    const header = `8=FIX.4.4|9=${body.length}|35=${msgType}|${body}`;
    const checksum = this.calculateChecksum(header);
    const message = `${header}|10=${checksum}|`;

    this.messageSequenceNumber++;
    return message;
  }

  createLogonMessage(heartbeatInterval: number = 30): string {
    return this.createMessage('A', {
      '98': '0', // EncryptMethod (None)
      '108': heartbeatInterval.toString(), // HeartBtInt
    });
  }

  createLogoutMessage(): string {
    return this.createMessage('5', {});
  }

  createHeartbeatMessage(): string {
    return this.createMessage('0', {});
  }

  createNewOrderSingle(order: OrderRequest): string {
    return this.createMessage('D', {
      '11': order.clientOrderId, // ClOrdID
      '55': order.symbol, // Symbol
      '54': order.side === OrderSide.BUY ? '1' : '2', // Side
      '60': this.getTimestamp(), // TransactTime
      '38': order.quantity.toString(), // OrderQty
      '40': this.getOrderType(order.type), // OrdType
      '44': order.price?.toString() || '', // Price
      '59': this.getTimeInForce(order.timeInForce), // TimeInForce
    });
  }

  createOrderCancelRequest(orderId: string, symbol: string): string {
    return this.createMessage('F', {
      '11': `CANCEL_${Date.now()}`, // ClOrdID
      '41': orderId, // OrigClOrdID
      '55': symbol, // Symbol
      '60': this.getTimestamp(), // TransactTime
    });
  }

  parseMessage(message: string): Record<string, string> {
    const fields: Record<string, string> = {};
    const parts = message.split('|');

    for (const part of parts) {
      const [tag, value] = part.split('=');
      if (tag && value) {
        fields[tag] = value;
      }
    }

    return fields;
  }

  private getTimestamp(): string {
    const now = new Date();
    return now.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}Z/, '');
  }

  private calculateChecksum(message: string): string {
    let sum = 0;
    for (let i = 0; i < message.length; i++) {
      sum += message.charCodeAt(i);
    }
    const checksum = (sum % 256).toString().padStart(3, '0');
    return checksum;
  }

  private getOrderType(type: OrderType): string {
    switch (type) {
      case OrderType.MARKET:
        return '1';
      case OrderType.LIMIT:
        return '2';
      case OrderType.STOP:
        return '3';
      case OrderType.STOP_LIMIT:
        return '4';
      default:
        return '1';
    }
  }

  private getTimeInForce(tif: TimeInForce): string {
    switch (tif) {
      case TimeInForce.DAY:
        return '0';
      case TimeInForce.GTC:
        return '1';
      case TimeInForce.IOC:
        return '3';
      case TimeInForce.FOK:
        return '4';
      default:
        return '0';
    }
  }

  startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      const heartbeat = this.createHeartbeatMessage();
      this.emit('sendMessage', heartbeat);
    }, this.heartbeatIntervalMs);
  }

  stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}
```

## Low-Latency API Design Patterns

### Connection Pooling and Keep-Alive

```typescript
import http from 'http';
import https from 'https';
import axios from 'axios';

class LowLatencyHTTPClient {
  private readonly agent: http.Agent | https.Agent;

  constructor(baseURL: string, maxSockets: number = 100) {
    const isHttps = baseURL.startsWith('https');

    this.agent = isHttps
      ? new https.Agent({
          keepAlive: true,
          keepAliveMsecs: 1000,
          maxSockets: maxSockets,
          maxFreeSockets: 10,
          timeout: 30000,
          scheduling: 'fifo',
        })
      : new http.Agent({
          keepAlive: true,
          keepAliveMsecs: 1000,
          maxSockets: maxSockets,
          maxFreeSockets: 10,
          timeout: 30000,
          scheduling: 'fifo',
        });
  }

  createClient(baseURL: string): any {
    return axios.create({
      baseURL,
      httpAgent: this.agent,
      httpsAgent: this.agent,
      timeout: 5000,
      maxRedirects: 0,
    });
  }

  destroy(): void {
    this.agent.destroy();
  }
}
```

### Request Batching

```typescript
class BatchingOrderService {
  private pendingOrders: OrderRequest[] = [];
  private batchTimer: NodeJS.Timeout | null = null;
  private readonly batchSize: number = 10;
  private readonly batchDelayMs: number = 100;

  constructor(private readonly apiClient: any) {}

  async submitOrder(order: OrderRequest): Promise<void> {
    this.pendingOrders.push(order);

    if (this.pendingOrders.length >= this.batchSize) {
      await this.flushBatch();
    } else if (!this.batchTimer) {
      this.batchTimer = setTimeout(() => this.flushBatch(), this.batchDelayMs);
    }
  }

  private async flushBatch(): Promise<void> {
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    if (this.pendingOrders.length === 0) {
      return;
    }

    const batch = this.pendingOrders;
    this.pendingOrders = [];

    try {
      await this.apiClient.post('/api/v1/orders/batch', {
        orders: batch,
      });
    } catch (error) {
      console.error('Batch order submission failed:', error);
      // Handle error - potentially retry individual orders
    }
  }
}
```

### Binary Protocol for Ultra-Low Latency

```typescript
class BinaryOrderProtocol {
  encodeOrder(order: OrderRequest): Buffer {
    const buffer = Buffer.allocUnsafe(128);
    let offset = 0;

    // Message type (1 byte)
    buffer.writeUInt8(1, offset);
    offset += 1;

    // Client Order ID (8 bytes)
    const orderId = BigInt(order.clientOrderId);
    buffer.writeBigUInt64LE(orderId, offset);
    offset += 8;

    // Symbol (16 bytes, padded)
    buffer.write(order.symbol.padEnd(16, '\0'), offset, 16, 'ascii');
    offset += 16;

    // Side (1 byte)
    buffer.writeUInt8(order.side === OrderSide.BUY ? 1 : 2, offset);
    offset += 1;

    // Order Type (1 byte)
    buffer.writeUInt8(this.encodeOrderType(order.type), offset);
    offset += 1;

    // Quantity (8 bytes, double)
    buffer.writeDoubleLE(order.quantity, offset);
    offset += 8;

    // Price (8 bytes, double)
    buffer.writeDoubleLE(order.price || 0, offset);
    offset += 8;

    // Time in Force (1 byte)
    buffer.writeUInt8(this.encodeTimeInForce(order.timeInForce), offset);
    offset += 1;

    // Timestamp (8 bytes)
    buffer.writeBigUInt64LE(BigInt(Date.now()), offset);
    offset += 8;

    return buffer.slice(0, offset);
  }

  decodeOrder(buffer: Buffer): Order {
    let offset = 0;

    // Message type
    const msgType = buffer.readUInt8(offset);
    offset += 1;

    // Order ID
    const orderId = buffer.readBigUInt64LE(offset).toString();
    offset += 8;

    // Symbol
    const symbol = buffer.toString('ascii', offset, offset + 16).replace(/\0/g, '');
    offset += 16;

    // Side
    const side = buffer.readUInt8(offset) === 1 ? OrderSide.BUY : OrderSide.SELL;
    offset += 1;

    // Order Type
    const type = this.decodeOrderType(buffer.readUInt8(offset));
    offset += 1;

    // Quantity
    const quantity = buffer.readDoubleLE(offset);
    offset += 8;

    // Price
    const price = buffer.readDoubleLE(offset);
    offset += 8;

    // Time in Force
    const timeInForce = this.decodeTimeInForce(buffer.readUInt8(offset));
    offset += 1;

    // Timestamp
    const timestamp = Number(buffer.readBigUInt64LE(offset));
    offset += 8;

    return {
      orderId,
      clientOrderId: orderId,
      symbol,
      side,
      type,
      quantity,
      price: price || undefined,
      timeInForce,
      status: OrderStatus.PENDING,
      filledQuantity: 0,
      createdAt: new Date(timestamp),
      updatedAt: new Date(timestamp),
    };
  }

  private encodeOrderType(type: OrderType): number {
    const map: Record<OrderType, number> = {
      [OrderType.MARKET]: 1,
      [OrderType.LIMIT]: 2,
      [OrderType.STOP]: 3,
      [OrderType.STOP_LIMIT]: 4,
      [OrderType.TRAILING_STOP]: 5,
      [OrderType.ICEBERG]: 6,
      [OrderType.TWAP]: 7,
      [OrderType.VWAP]: 8,
    };
    return map[type] || 1;
  }

  private decodeOrderType(value: number): OrderType {
    const map: Record<number, OrderType> = {
      1: OrderType.MARKET,
      2: OrderType.LIMIT,
      3: OrderType.STOP,
      4: OrderType.STOP_LIMIT,
      5: OrderType.TRAILING_STOP,
      6: OrderType.ICEBERG,
      7: OrderType.TWAP,
      8: OrderType.VWAP,
    };
    return map[value] || OrderType.MARKET;
  }

  private encodeTimeInForce(tif: TimeInForce): number {
    const map: Record<TimeInForce, number> = {
      [TimeInForce.DAY]: 1,
      [TimeInForce.GTC]: 2,
      [TimeInForce.IOC]: 3,
      [TimeInForce.FOK]: 4,
      [TimeInForce.GTD]: 5,
    };
    return map[tif] || 1;
  }

  private decodeTimeInForce(value: number): TimeInForce {
    const map: Record<number, TimeInForce> = {
      1: TimeInForce.DAY,
      2: TimeInForce.GTC,
      3: TimeInForce.IOC,
      4: TimeInForce.FOK,
      5: TimeInForce.GTD,
    };
    return map[value] || TimeInForce.DAY;
  }
}
```

## Risk Check Integration

### Pre-Trade Risk Checks

```typescript
interface RiskLimits {
  maxOrderSize: number;
  maxPositionSize: number;
  maxDailyLoss: number;
  maxDailyVolume: number;
  allowedSymbols: string[];
  blockedSymbols: string[];
}

class RiskManager {
  private readonly limits: RiskLimits;
  private positions: Map<string, number> = new Map();
  private dailyVolume: number = 0;
  private dailyPnL: number = 0;

  constructor(limits: RiskLimits) {
    this.limits = limits;
  }

  async validateOrder(order: OrderRequest): Promise<void> {
    // Check symbol is allowed
    if (this.limits.blockedSymbols.includes(order.symbol)) {
      throw new RiskError(`Symbol ${order.symbol} is blocked`);
    }

    if (
      this.limits.allowedSymbols.length > 0 &&
      !this.limits.allowedSymbols.includes(order.symbol)
    ) {
      throw new RiskError(`Symbol ${order.symbol} is not in allowed list`);
    }

    // Check order size
    if (order.quantity > this.limits.maxOrderSize) {
      throw new RiskError(
        `Order size ${order.quantity} exceeds maximum ${this.limits.maxOrderSize}`
      );
    }

    // Check position limits
    const currentPosition = this.positions.get(order.symbol) || 0;
    const newPosition =
      currentPosition +
      (order.side === OrderSide.BUY ? order.quantity : -order.quantity);

    if (Math.abs(newPosition) > this.limits.maxPositionSize) {
      throw new RiskError(
        `Position would exceed maximum ${this.limits.maxPositionSize}`
      );
    }

    // Check daily volume
    const orderValue = order.quantity * (order.price || 0);
    if (this.dailyVolume + orderValue > this.limits.maxDailyVolume) {
      throw new RiskError('Daily volume limit exceeded');
    }

    // Check daily loss limit
    if (this.dailyPnL < -this.limits.maxDailyLoss) {
      throw new RiskError('Daily loss limit exceeded');
    }
  }

  updatePosition(symbol: string, quantity: number, side: OrderSide): void {
    const current = this.positions.get(symbol) || 0;
    const delta = side === OrderSide.BUY ? quantity : -quantity;
    this.positions.set(symbol, current + delta);
  }

  updateDailyMetrics(volume: number, pnl: number): void {
    this.dailyVolume += volume;
    this.dailyPnL += pnl;
  }

  resetDailyMetrics(): void {
    this.dailyVolume = 0;
    this.dailyPnL = 0;
  }

  getPosition(symbol: string): number {
    return this.positions.get(symbol) || 0;
  }

  getAllPositions(): Map<string, number> {
    return new Map(this.positions);
  }
}

class RiskError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RiskError';
  }
}
```

### Dynamic Risk Adjustment

```typescript
class DynamicRiskManager extends RiskManager {
  private volatilityAdjustments: Map<string, number> = new Map();

  async validateOrder(order: OrderRequest): Promise<void> {
    // Apply base risk checks
    await super.validateOrder(order);

    // Apply volatility-based adjustments
    const volatilityFactor = this.volatilityAdjustments.get(order.symbol) || 1.0;
    const adjustedMaxSize = this.limits.maxOrderSize / volatilityFactor;

    if (order.quantity > adjustedMaxSize) {
      throw new RiskError(
        `Order size ${order.quantity} exceeds volatility-adjusted maximum ${adjustedMaxSize}`
      );
    }
  }

  updateVolatilityAdjustment(symbol: string, volatility: number): void {
    // Higher volatility = lower position limits
    const factor = Math.max(1.0, volatility / 0.02); // Normalize to 2% baseline
    this.volatilityAdjustments.set(symbol, factor);
  }
}
```

## Position and Account APIs

### Position Management

```typescript
interface Position {
  symbol: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  realizedPnL: number;
  side: 'LONG' | 'SHORT' | 'FLAT';
}

class PositionService {
  private readonly apiClient: any;

  constructor(apiClient: any) {
    this.apiClient = apiClient;
  }

  async getPositions(): Promise<Position[]> {
    const response = await this.apiClient.get('/api/v1/positions');

    return response.data.map((p: any) => ({
      symbol: p.symbol,
      quantity: parseFloat(p.quantity),
      averagePrice: parseFloat(p.avgPrice),
      currentPrice: parseFloat(p.currentPrice),
      unrealizedPnL: parseFloat(p.unrealizedPnL),
      realizedPnL: parseFloat(p.realizedPnL),
      side: parseFloat(p.quantity) > 0 ? 'LONG' : parseFloat(p.quantity) < 0 ? 'SHORT' : 'FLAT',
    }));
  }

  async getPosition(symbol: string): Promise<Position | null> {
    try {
      const response = await this.apiClient.get(`/api/v1/positions/${symbol}`);

      return {
        symbol: response.data.symbol,
        quantity: parseFloat(response.data.quantity),
        averagePrice: parseFloat(response.data.avgPrice),
        currentPrice: parseFloat(response.data.currentPrice),
        unrealizedPnL: parseFloat(response.data.unrealizedPnL),
        realizedPnL: parseFloat(response.data.realizedPnL),
        side: parseFloat(response.data.quantity) > 0 ? 'LONG' : parseFloat(response.data.quantity) < 0 ? 'SHORT' : 'FLAT',
      };
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async closePosition(symbol: string): Promise<Order> {
    const position = await this.getPosition(symbol);

    if (!position || position.quantity === 0) {
      throw new Error(`No open position for ${symbol}`);
    }

    const side = position.quantity > 0 ? OrderSide.SELL : OrderSide.BUY;
    const quantity = Math.abs(position.quantity);

    const orderService = new TradingOrderService(this.apiClient, new RiskManager({
      maxOrderSize: 1000000,
      maxPositionSize: 1000000,
      maxDailyLoss: 100000,
      maxDailyVolume: 10000000,
      allowedSymbols: [],
      blockedSymbols: [],
    }));

    return orderService.placeOrder({
      clientOrderId: `CLOSE_${symbol}_${Date.now()}`,
      symbol,
      side,
      type: OrderType.MARKET,
      quantity,
      timeInForce: TimeInForce.IOC,
    });
  }
}
```

### Account Information

```typescript
interface AccountInfo {
  accountId: string;
  balance: number;
  availableBalance: number;
  marginUsed: number;
  marginAvailable: number;
  totalEquity: number;
  unrealizedPnL: number;
  realizedPnL: number;
  leverage: number;
}

class AccountService {
  private readonly apiClient: any;

  constructor(apiClient: any) {
    this.apiClient = apiClient;
  }

  async getAccountInfo(): Promise<AccountInfo> {
    const response = await this.apiClient.get('/api/v1/account');

    return {
      accountId: response.data.accountId,
      balance: parseFloat(response.data.balance),
      availableBalance: parseFloat(response.data.availableBalance),
      marginUsed: parseFloat(response.data.marginUsed),
      marginAvailable: parseFloat(response.data.marginAvailable),
      totalEquity: parseFloat(response.data.totalEquity),
      unrealizedPnL: parseFloat(response.data.unrealizedPnL),
      realizedPnL: parseFloat(response.data.realizedPnL),
      leverage: parseFloat(response.data.leverage),
    };
  }

  async getAccountHistory(
    startTime?: Date,
    endTime?: Date
  ): Promise<AccountTransaction[]> {
    const response = await this.apiClient.get('/api/v1/account/history', {
      params: {
        startTime: startTime?.getTime(),
        endTime: endTime?.getTime(),
      },
    });

    return response.data.map((t: any) => ({
      id: t.id,
      type: t.type,
      amount: parseFloat(t.amount),
      balance: parseFloat(t.balance),
      timestamp: new Date(t.timestamp),
      description: t.description,
    }));
  }
}

interface AccountTransaction {
  id: string;
  type: string;
  amount: number;
  balance: number;
  timestamp: Date;
  description: string;
}
```

## Error Handling and Retry Logic

```typescript
enum TradingErrorType {
  INSUFFICIENT_BALANCE = 'INSUFFICIENT_BALANCE',
  INVALID_SYMBOL = 'INVALID_SYMBOL',
  ORDER_NOT_FOUND = 'ORDER_NOT_FOUND',
  MARKET_CLOSED = 'MARKET_CLOSED',
  RATE_LIMIT = 'RATE_LIMIT',
  NETWORK_ERROR = 'NETWORK_ERROR',
  REJECTED_BY_EXCHANGE = 'REJECTED_BY_EXCHANGE',
  POSITION_LIMIT_EXCEEDED = 'POSITION_LIMIT_EXCEEDED',
}

class TradingError extends Error {
  constructor(
    public type: TradingErrorType,
    public message: string,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'TradingError';
  }
}

class TradingErrorHandler {
  static handleError(error: any): TradingError {
    const apiError = error.response?.data;

    if (!apiError) {
      return new TradingError(
        TradingErrorType.NETWORK_ERROR,
        'Network error occurred',
        true
      );
    }

    switch (apiError.code) {
      case 'INSUFFICIENT_BALANCE':
        return new TradingError(
          TradingErrorType.INSUFFICIENT_BALANCE,
          'Insufficient balance for order',
          false
        );

      case 'MARKET_CLOSED':
        return new TradingError(
          TradingErrorType.MARKET_CLOSED,
          'Market is currently closed',
          false
        );

      case 'RATE_LIMIT':
        return new TradingError(
          TradingErrorType.RATE_LIMIT,
          'Rate limit exceeded',
          true
        );

      default:
        return new TradingError(
          TradingErrorType.REJECTED_BY_EXCHANGE,
          apiError.message || 'Order rejected by exchange',
          false
        );
    }
  }
}

class TradingRetryHandler {
  private readonly maxRetries: number = 3;
  private readonly baseDelay: number = 1000;

  async executeWithRetry<T>(
    operation: () => Promise<T>,
    retryableErrors: TradingErrorType[]
  ): Promise<T> {
    let lastError: TradingError;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = TradingErrorHandler.handleError(error);

        if (!lastError.retryable || !retryableErrors.includes(lastError.type)) {
          throw lastError;
        }

        if (attempt === this.maxRetries) {
          throw lastError;
        }

        const delay = this.baseDelay * Math.pow(2, attempt);
        console.log(`Retrying after ${delay}ms (attempt ${attempt + 1}/${this.maxRetries})`);
        await this.sleep(delay);
      }
    }

    throw lastError!;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}
```

## Rate Limiting Patterns

```typescript
class TokenBucketRateLimiter {
  private tokens: number;
  private readonly capacity: number;
  private readonly refillRate: number; // tokens per second
  private lastRefill: number;

  constructor(capacity: number, refillRate: number) {
    this.capacity = capacity;
    this.refillRate = refillRate;
    this.tokens = capacity;
    this.lastRefill = Date.now();
  }

  async acquire(tokens: number = 1): Promise<void> {
    this.refill();

    while (this.tokens < tokens) {
      const waitTime = ((tokens - this.tokens) / this.refillRate) * 1000;
      await this.sleep(waitTime);
      this.refill();
    }

    this.tokens -= tokens;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    const tokensToAdd = elapsed * this.refillRate;

    this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
    this.lastRefill = now;
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

class RateLimitedTradingClient {
  private readonly orderRateLimiter: TokenBucketRateLimiter;
  private readonly marketDataRateLimiter: TokenBucketRateLimiter;

  constructor() {
    this.orderRateLimiter = new TokenBucketRateLimiter(50, 10); // 50 capacity, 10/sec
    this.marketDataRateLimiter = new TokenBucketRateLimiter(200, 100); // 200 capacity, 100/sec
  }

  async placeOrder(order: OrderRequest): Promise<Order> {
    await this.orderRateLimiter.acquire();
    // Place order logic
    return {} as Order;
  }

  async getMarketData(symbol: string): Promise<Ticker> {
    await this.marketDataRateLimiter.acquire();
    // Get market data logic
    return {} as Ticker;
  }
}
```

## Security Considerations

```typescript
import crypto from 'crypto';

class SecureTradingClient {
  private readonly apiKey: string;
  private readonly apiSecret: string;

  constructor(apiKey: string, apiSecret: string) {
    this.apiKey = apiKey;
    this.apiSecret = apiSecret;
  }

  signRequest(method: string, path: string, body: string, timestamp: number): string {
    const payload = `${timestamp}${method}${path}${body}`;
    return crypto
      .createHmac('sha256', this.apiSecret)
      .update(payload)
      .digest('hex');
  }

  createAuthHeaders(method: string, path: string, body: string = ''): Record<string, string> {
    const timestamp = Date.now();
    const signature = this.signRequest(method, path, body, timestamp);

    return {
      'X-API-KEY': this.apiKey,
      'X-TIMESTAMP': timestamp.toString(),
      'X-SIGNATURE': signature,
    };
  }
}
```

## Production-Grade Practices

```typescript
import winston from 'winston';

class TradingLogger {
  private logger: winston.Logger;

  constructor() {
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      transports: [
        new winston.transports.File({ filename: 'trading-error.log', level: 'error' }),
        new winston.transports.File({ filename: 'trading-audit.log' }),
      ],
    });
  }

  logOrderPlacement(order: OrderRequest): void {
    this.logger.info('Order placed', {
      clientOrderId: order.clientOrderId,
      symbol: order.symbol,
      side: order.side,
      type: order.type,
      quantity: order.quantity,
      price: order.price,
    });
  }

  logOrderFill(order: Order): void {
    this.logger.info('Order filled', {
      orderId: order.orderId,
      symbol: order.symbol,
      filledQuantity: order.filledQuantity,
      averagePrice: order.averagePrice,
    });
  }
}
```

## Provider Examples

### Interactive Brokers TWS API

```typescript
class InteractiveBrokersClient {
  async placeOrder(order: OrderRequest): Promise<Order> {
    // IB TWS API integration
    return {} as Order;
  }
}
```

### Coinbase Pro API

```typescript
class CoinbaseProClient {
  async placeOrder(order: OrderRequest): Promise<Order> {
    // Coinbase Pro API integration
    return {} as Order;
  }
}
```

### Binance API

```typescript
class BinanceClient {
  async placeOrder(order: OrderRequest): Promise<Order> {
    // Binance API integration
    return {} as Order;
  }
}
```

## Conclusion

Trading API integration requires careful attention to performance, reliability, and risk management. Key takeaways:

1. **Low Latency**: Use connection pooling, batching, and binary protocols
2. **Risk Management**: Implement comprehensive pre-trade checks
3. **Real-Time Data**: Use WebSocket connections for market data
4. **Audit Trail**: Log all trading activity
5. **Error Handling**: Implement proper retry logic
6. **Rate Limiting**: Respect API limits
7. **Security**: Sign all requests and protect API credentials

Always test thoroughly in sandbox environments and implement comprehensive monitoring for production systems.
