"""Payment orchestration with multiple processors"""
import logging

class PaymentOrchestrator:
    def __init__(self, processors_config, payment_router):
        self.processors = processors_config
        self.router = payment_router
        self.logger = logging.getLogger(__name__)

    async def process_payment(self, request):
        """Orchestrate payment through optimal processor"""
        # Determine best processor
        processor_name = self.router.select(request)
        processors_list = self.router.get_fallback_chain(processor_name)
        
        # Try each processor in chain
        for proc_name in processors_list:
            try:
                result = await self._charge_processor(proc_name, request)
                if result['success']:
                    return {'processor': proc_name, **result}
                elif not self._should_fallback(result):
                    return {'processor': proc_name, **result}
            except Exception as e:
                self.logger.warning(f"Processor {proc_name} failed: {e}")
                continue
        
        return {'success': False, 'error': 'All processors failed'}

    async def _charge_processor(self, processor_name, request):
        processor = self.processors[processor_name]
        return await processor.authorize(request)

    def _should_fallback(self, result):
        retryable = ['timeout', 'unavailable', 'try_again']
        return result.get('code') in retryable
