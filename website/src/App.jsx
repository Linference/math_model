import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Docs from './pages/Docs'
import Changelog from './pages/Changelog'
import Thanks from './pages/Thanks'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/changelog" element={<Changelog />} />
        <Route path="/thanks" element={<Thanks />} />
      </Route>
    </Routes>
  )
}
