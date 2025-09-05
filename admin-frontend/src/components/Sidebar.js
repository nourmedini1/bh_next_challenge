import React from 'react';
import { Button } from 'react-bootstrap';
import { 
  BsGear,
  BsDatabase,
  BsBarChart,
  BsList,
  BsX,
  BsPersonCircle,
  BsTag,
  BsBookmark,
  BsFileText,
  BsMap
} from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';

const Sidebar = ({ activeSection, setActiveSection, isCollapsed, setIsCollapsed, isMobile }) => {
  const { isDarkMode } = useTheme();

  const handleNavClick = (sectionId) => {
    setActiveSection(sectionId);
    // Auto-close sidebar on mobile when item is selected
    if (isMobile) {
      setIsCollapsed(true);
    }
  };
  const menuItems = [
    { id: 'vector-stores', label: 'Vector Stores', icon: BsDatabase },
    { id: 'analytics', label: 'Analytics', icon: BsBarChart },
    { id: 'agents', label: 'Agents', icon: BsPersonCircle },
    { id: 'tags', label: 'Tags', icon: BsTag },
    { id: 'terms', label: 'Terms', icon: BsBookmark },
    { id: 'guidelines', label: 'Guidelines', icon: BsFileText },
    { id: 'journeys', label: 'Journeys', icon: BsMap },
    { id: 'settings', label: 'Settings', icon: BsGear },
  ];

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : 'expanded'} ${isDarkMode ? 'dark-theme' : 'light-theme'}`}>
      <div className="navigation-menu">
        {/* Toggle button positioned like a nav item when collapsed */}
        <Button
          className="sidebar-toggle-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
        >
          {isCollapsed ? <BsList size={20} /> : <BsX size={20} />}
        </Button>
        
        {menuItems.map((item) => {
          const IconComponent = item.icon;
          const isActive = activeSection === item.id;
          
          return (
            <div
              key={item.id}
              className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
              onClick={() => handleNavClick(item.id)}
            >
              <IconComponent className="nav-icon" />
              <span className="nav-text">{item.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Sidebar;
