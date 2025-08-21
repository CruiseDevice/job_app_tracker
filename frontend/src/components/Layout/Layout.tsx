import clsx from "clsx";
import { useAppSelector } from '../../hooks/useAppSelector';
import { Circle } from "lucide-react";
import { Link, useLocation } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { is_monitoring } = useAppSelector((state) => state.monitor); 
  const location = useLocation();
  const navigation = [
    {name: 'Dashboard', href:'/', icon: 'Home'},
    {name: 'Applications', href:'/applications', icon: 'FileText'},
    {name: 'Settings', href:'/settings', icon: 'Settings'},
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Smart Job Tracker
              </h1>
            </div>
            <div className="flex items-center space-x-2">
              <Circle 
                className={clsx('w-3 h-3', {
                  'text-green-500 fill-current': is_monitoring,
                  'text-red-500 fill-current': !is_monitoring,
                })}
              />
              <span className="text-sm text-gray-600">
                {is_monitoring ? 'Monitoring Active' : 'Monitoring Inactive'}
              </span>
            </div>
          </div>
        </div>
      </header>
      <div className="flex">
        {/* sidebar */}
        <nav className="w-64 bg-white shadow-sm min-h-screen">
          <div className="p-4">
            <ul className="space-y-2">
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;

                return (
                  <li key={item.name}>
                    <Link
                      to={item.href}
                      className={clsx('flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors', {
                        'bg-blue-100 text-blue-700': isActive,
                        'text-gray-600 hover:text-gray-900 hover:bg-gray-50': !isActive,
                      }
                    )}
                    >
                    <Icon />
                    {item.name}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        </nav>
        {/* main content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout;