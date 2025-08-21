import Layout from './components/Layout/Layout';
import './App.css'
import { Route, Routes } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />}></Route>
      </Routes>
    </Layout>
  )
}

export default App
