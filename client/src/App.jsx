import { Routes, Route, Navigate } from 'react-router-dom'
import { Container } from 'react-bootstrap'
import Header from './components/Header'
// import Dashboard from './components/Dashboard'
import QueryForm from './components/QueryForm'
// import ChartDisplay from './components/ChartDisplay'
// import InventoryCheck from './components/InventoryCheck'
// import ReportGenerator from './components/ReportGenerator'
import DataSourceManager from './components/DataSourceManager'

function App() {
  return (
    <>
      <Header />
      <Container fluid className="py-4">
        <Routes>
          {/* <Route path="/" element={<Dashboard />} /> */}
          <Route path="/" element={<Navigate replace to="/query" />} />
          <Route path="/query" element={<QueryForm />} />
          {/* <Route path="/inventory" element={<InventoryCheck />} /> */}
          {/* <Route path="/charts" element={<ChartDisplay />} /> */}
          {/* <Route path="/reports" element={<ReportGenerator />} /> */}
          <Route path="/datasources" element={<DataSourceManager />} />
        </Routes>
      </Container>
    </>
  )
}

export default App 