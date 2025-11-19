import React, { useState } from 'react'
import PlaygroundIndex from './pages/PlaygroundIndex'
import BasicExample from './pages/BasicExample'
import AdvancedExample from './pages/AdvancedExample'
import FormExample from './pages/FormExample'
import ErrorHandling from './pages/ErrorHandling'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('index')

  const pages = {
    index: PlaygroundIndex,
    basic: BasicExample,
    advanced: AdvancedExample,
    form: FormExample,
    errors: ErrorHandling,
  }

  const CurrentPage = pages[currentPage]

  return (
    <div className="app">
      <header className="app-header">
        <h1>Interactive API Integration Playground</h1>
        <p>Learn API integration with live, runnable examples</p>
      </header>

      <nav className="app-nav">
        <button
          className={currentPage === 'index' ? 'active' : ''}
          onClick={() => setCurrentPage('index')}
        >
          Home
        </button>
        <button
          className={currentPage === 'basic' ? 'active' : ''}
          onClick={() => setCurrentPage('basic')}
        >
          Basic Fetch
        </button>
        <button
          className={currentPage === 'advanced' ? 'active' : ''}
          onClick={() => setCurrentPage('advanced')}
        >
          Advanced State
        </button>
        <button
          className={currentPage === 'form' ? 'active' : ''}
          onClick={() => setCurrentPage('form')}
        >
          Form Integration
        </button>
        <button
          className={currentPage === 'errors' ? 'active' : ''}
          onClick={() => setCurrentPage('errors')}
        >
          Error Handling
        </button>
      </nav>

      <main className="app-main">
        <CurrentPage />
      </main>

      <footer className="app-footer">
        <p>Interactive Playground - Learn by doing. Experiment with the code!</p>
      </footer>
    </div>
  )
}

export default App
