import CustomerPortal from './pages/CustomerPortal';
import AdminMonitor from './pages/AdminMonitor';

export default function App() {
  const path = window.location.pathname.toLowerCase();
  const hash = window.location.hash.toLowerCase();

  if (path.startsWith('/admin') || hash.startsWith('#/admin')) {
    return <AdminMonitor />;
  }

  return <CustomerPortal />;
}