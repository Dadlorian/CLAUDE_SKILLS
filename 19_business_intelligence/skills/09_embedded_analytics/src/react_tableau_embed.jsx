import React, { useEffect, useState, useRef } from 'react';

/**
 * Production-ready Tableau embedding component
 * Features: Token management, error handling, cleanup
 */
export function TableauDashboard({ dashboardId, filters = {}, onLoad, onError }) {
  const containerRef = useRef(null);
  const vizRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTableauViz();

    return () => {
      // Cleanup: dispose viz to prevent memory leaks
      if (vizRef.current) {
        vizRef.current.dispose();
        vizRef.current = null;
      }
    };
  }, [dashboardId]);

  async function loadTableauViz() {
    try {
      setLoading(true);
      setError(null);

      // Fetch embed token
      const response = await fetch('/api/tableau-token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dashboardId }),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(`Token request failed: ${response.statusText}`);
      }

      const { token, embedUrl } = await response.json();

      // Load Tableau SDK if not already loaded
      if (!window.tableau) {
        await loadTableauSDK();
      }

      // Configure embedding options
      const options = {
        width: '100%',
        height: '800px',
        hideTabs: true,
        hideToolbar: false,
        device: window.innerWidth < 768 ? 'phone' : 'desktop',
        onFirstInteractive: handleFirstInteractive
      };

      // Create viz
      const viz = new window.tableau.Viz(
        containerRef.current,
        embedUrl,
        options
      );

      vizRef.current = viz;

      // Apply filters if provided
      if (Object.keys(filters).length > 0) {
        viz.addEventListener(window.tableau.TableauEventName.FIRST_INTERACTIVE, () => {
          applyFilters(viz, filters);
        });
      }

    } catch (err) {
      console.error('Tableau embed error:', err);
      setError(err.message);
      onError?.(err);
    } finally {
      setLoading(false);
    }
  }

  function handleFirstInteractive() {
    console.log('Tableau viz interactive');
    setLoading(false);
    onLoad?.();
  }

  async function applyFilters(viz, filters) {
    const workbook = viz.getWorkbook();
    const activeSheet = workbook.getActiveSheet();

    for (const [fieldName, value] of Object.entries(filters)) {
      try {
        await activeSheet.applyFilterAsync(
          fieldName,
          Array.isArray(value) ? value : [value],
          window.tableau.FilterUpdateType.REPLACE
        );
      } catch (err) {
        console.warn(`Failed to apply filter ${fieldName}:`, err);
      }
    }
  }

  function loadTableauSDK() {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://tableau.example.com/javascripts/api/tableau-2.9.0.min.js';
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  if (error) {
    return (
      <div className="tableau-error">
        <h3>Failed to load dashboard</h3>
        <p>{error}</p>
        <button onClick={loadTableauViz}>Retry</button>
      </div>
    );
  }

  return (
    <div className="tableau-container">
      {loading && (
        <div className="tableau-loading">
          <div className="spinner" />
          <p>Loading dashboard...</p>
        </div>
      )}
      <div ref={containerRef} />
    </div>
  );
}

export default TableauDashboard;
