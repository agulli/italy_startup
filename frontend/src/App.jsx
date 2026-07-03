import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Search, MapPin, Users, ExternalLink, Globe } from 'lucide-react';

// Custom hook to fly to a location
function FlyToLocation({ location }) {
  const map = useMap();
  useEffect(() => {
    if (location) {
      map.flyTo(location, 13, { duration: 1.5 });
    }
  }, [location, map]);
  return null;
}

function App() {
  const [startups, setStartups] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [search, setSearch] = useState('');
  const [activeLocation, setActiveLocation] = useState(null);
  const [activeStartup, setActiveStartup] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the JSON payload built by the DB init script
    fetch('/startups.json')
      .then(res => res.json())
      .then(data => {
        setStartups(data);
        setFiltered(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load startups.json", err);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    const term = search.toLowerCase();
    const result = startups.filter(s => 
      (s.name && s.name.toLowerCase().includes(term)) || 
      (s.location && s.location.toLowerCase().includes(term)) ||
      (s.founders && s.founders.toLowerCase().includes(term))
    );
    setFiltered(result);
  }, [search, startups]);

  const handleSelect = (startup) => {
    setActiveStartup(startup);
    if (startup.lat && startup.lng) {
      setActiveLocation([startup.lat, startup.lng]);
    }
  };

  if (loading) {
    return <div className="loading-state">Loading startups...</div>;
  }

  return (
    <div className="app-container">
      {/* Sidebar Area */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h1>Italy Startups</h1>
          <p>Explore {startups.length} startups across Europe.</p>
          <div className="search-box">
            <Search className="search-icon" size={18} />
            <input 
              type="text" 
              className="search-input"
              placeholder="Search by name, city, or founder..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
        </div>
        
        <div className="startup-list">
          {filtered.length === 0 ? (
            <div className="empty-state">
              <p>No startups found matching "{search}"</p>
            </div>
          ) : (
            filtered.map((startup, idx) => (
              <div 
                key={idx} 
                className={`startup-item ${activeStartup === startup ? 'active' : ''}`}
                onClick={() => handleSelect(startup)}
              >
                <div className="startup-name">{startup.name !== 'N/A' && startup.name !== 'null' ? startup.name : 'Unknown Startup'}</div>
                <div className="startup-meta">
                  <div className="meta-item">
                    <MapPin size={14} />
                    {startup.location !== 'N/A' ? startup.location : 'Unknown'}
                  </div>
                </div>
                {startup.founders && startup.founders !== 'N/A' && startup.founders !== 'null' && (
                  <div className="startup-founders">
                    <Users size={12} style={{ display: 'inline', marginRight: 4, verticalAlign: '-1px' }}/>
                    {startup.founders}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Map Area */}
      <main className="map-container">
        <MapContainer 
          center={[41.8719, 12.5674]} 
          zoom={5} 
          scrollWheelZoom={true}
        >
          {/* Using CartoDB Dark Matter for premium dark aesthetic */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          
          <FlyToLocation location={activeLocation} />

          {startups.map((startup, idx) => {
            if (!startup.lat || !startup.lng) return null;
            return (
              <Marker 
                key={idx} 
                position={[startup.lat, startup.lng]}
                eventHandlers={{
                  click: () => handleSelect(startup),
                }}
              >
                <Popup>
                  <div className="popup-title">{startup.name !== 'N/A' && startup.name !== 'null' ? startup.name : 'Unknown Startup'}</div>
                  <div className="popup-meta">
                    <MapPin size={12} style={{ marginRight: 4, display: 'inline' }}/>
                    {startup.location}
                  </div>
                  {startup.founders && startup.founders !== 'N/A' && startup.founders !== 'null' && (
                    <div className="popup-meta" style={{ marginTop: 4 }}>
                      <strong>Founders:</strong> {startup.founders}
                    </div>
                  )}
                  <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {startup.website && startup.website !== 'N/A' && startup.website !== 'null' && (
                      <a href={startup.website} target="_blank" rel="noopener noreferrer" className="popup-link">
                        <Globe size={14} /> Visit Website
                      </a>
                    )}
                    {startup.article_url && startup.article_url !== 'N/A' && (
                      <a href={startup.article_url} target="_blank" rel="noopener noreferrer" className="popup-link">
                        <ExternalLink size={14} /> Read Article
                      </a>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </main>
    </div>
  );
}

export default App;
