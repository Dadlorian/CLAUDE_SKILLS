import React, { useState, useEffect } from 'react';
import { models } from 'powerbi-client';
import { PowerBIEmbed } from 'powerbi-client-react';

/**
 * Production-ready Power BI embedding component
 * Features: Auto token refresh, RLS, error handling
 */
export function PowerBIDashboard({ reportId, config = {}, onLoad, onError }) {
  const [embedConfig, setEmbedConfig] = useState(null);
  const [tokenExpiry, setTokenExpiry] = useState(null);

  useEffect(() => {
    fetchEmbedConfig();

    // Schedule token refresh before expiration
    const refreshInterval = setInterval(() => {
      if (tokenExpiry && Date.now() > tokenExpiry - 5 * 60 * 1000) {
        refreshToken();
      }
    }, 60 * 1000); // Check every minute

    return () => clearInterval(refreshInterval);
  }, [reportId]);

  async function fetchEmbedConfig() {
    try {
      const response = await fetch('/api/powerbi-embed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reportId,
          filters: config.filters
        }),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch embed config: ${response.statusText}`);
      }

      const data = await response.json();

      setEmbedConfig({
        type: 'report',
        tokenType: models.TokenType.Embed,
        accessToken: data.token,
        embedUrl: data.embedUrl,
        id: reportId,
        permissions: models.Permissions.Read,
        settings: {
          panes: {
            filters: { visible: config.showFilters ?? false },
            pageNavigation: { visible: config.showNavigation ?? true }
          },
          bars: {
            actionBar: { visible: config.showActionBar ?? false },
            statusBar: { visible: false }
          },
          background: models.BackgroundType.Transparent,
          layoutType: models.LayoutType.Custom,
          customLayout: {
            displayOption: models.DisplayOption.FitToPage
          }
        },
        filters: config.filters || []
      });

      setTokenExpiry(new Date(data.expiration).getTime());

    } catch (error) {
      console.error('Power BI embed error:', error);
      onError?.(error);
    }
  }

  async function refreshToken() {
    console.log('Refreshing Power BI token...');
    await fetchEmbedConfig();
  }

  const handleLoad = () => {
    console.log('Power BI report loaded');
    onLoad?.();
  };

  const handleError = (error) => {
    console.error('Power BI error:', error);
    onError?.(error);
  };

  if (!embedConfig) {
    return <div className="powerbi-loading">Loading report...</div>;
  }

  return (
    <div className="powerbi-container">
      <PowerBIEmbed
        embedConfig={embedConfig}
        eventHandlers={new Map([
          ['loaded', handleLoad],
          ['error', handleError],
          ['rendered', () => console.log('Report rendered')]
        ])}
        cssClassName="powerbi-report"
        getEmbeddedComponent={(embeddedReport) => {
          window.report = embeddedReport;
        }}
      />
    </div>
  );
}

export default PowerBIDashboard;
