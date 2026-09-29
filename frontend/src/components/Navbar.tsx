import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, BookOpen, Sparkles, LogOut, User, Menu, X } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/',      label: 'Villas',      icon: Home },
  { to: '/bookings', label: 'My Bookings', icon: BookOpen },
  { to: '/rag',   label: 'Data AI',     icon: Sparkles },
];

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'rgba(255,255,255,0.92)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
    }}>
      <nav style={{
        maxWidth: '1280px', margin: '0 auto',
        padding: '0 1.5rem',
        height: '64px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        gap: '2rem',
      }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
          <div style={{
            width: 32, height: 32,
            background: 'var(--accent)',
            borderRadius: 8,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <Home size={16} color="#fff" strokeWidth={2.5} />
          </div>
          <span style={{
            fontWeight: 800, fontSize: '1.1rem',
            color: 'var(--text-primary)', letterSpacing: '-0.03em',
          }}>
            Villa<span style={{ color: 'var(--accent)' }}>Stay</span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}
             className="desktop-nav">
          {navItems.map(({ to, label, icon: Icon }) => {
            const active = isActive(to);
            return (
              <Link key={to} to={to} style={{
                display: 'flex', alignItems: 'center', gap: '0.4rem',
                padding: '0.5rem 0.875rem',
                borderRadius: 8,
                fontWeight: active ? 600 : 500,
                fontSize: '0.9rem',
                color: active ? 'var(--accent)' : 'var(--text-secondary)',
                background: active ? 'var(--accent-light)' : 'transparent',
                textDecoration: 'none',
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => { if (!active) (e.currentTarget as HTMLElement).style.background = 'var(--surface-2)'; }}
              onMouseLeave={e => { if (!active) (e.currentTarget as HTMLElement).style.background = 'transparent'; }}>
                <Icon size={15} strokeWidth={2} />
                {label}
              </Link>
            );
          })}
        </div>

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }} className="desktop-nav">
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.625rem',
            padding: '0.375rem 0.625rem 0.375rem 0.5rem',
            borderRadius: 8, border: '1px solid var(--border)',
            cursor: 'pointer', transition: 'all 0.15s',
          }}
          onClick={handleLogout}
          title="Sign out"
          onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = 'var(--error-light)'}
          onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = 'transparent'}>
            <div style={{
              width: 28, height: 28, borderRadius: '50%',
              background: 'var(--accent-light)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <User size={14} color="var(--accent)" strokeWidth={2.5} />
            </div>
            <LogOut size={14} color="var(--text-muted)" strokeWidth={2} />
          </div>
        </div>

        {/* Mobile hamburger */}
        <button
          className="mobile-menu-btn"
          onClick={() => setMenuOpen(!menuOpen)}
          style={{
            display: 'none', background: 'none', border: 'none',
            cursor: 'pointer', padding: 8, borderRadius: 8, color: 'var(--text-primary)',
          }}>
          {menuOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="mobile-menu" style={{
          background: 'var(--surface)',
          borderTop: '1px solid var(--border)',
          padding: '1rem 1.5rem',
          display: 'flex', flexDirection: 'column', gap: '0.25rem',
        }}>
          {navItems.map(({ to, label, icon: Icon }) => {
            const active = isActive(to);
            return (
              <Link key={to} to={to}
                onClick={() => setMenuOpen(false)}
                style={{
                  display: 'flex', alignItems: 'center', gap: '0.625rem',
                  padding: '0.75rem 1rem', borderRadius: 8,
                  fontWeight: active ? 600 : 500,
                  fontSize: '0.9375rem',
                  color: active ? 'var(--accent)' : 'var(--text-secondary)',
                  background: active ? 'var(--accent-light)' : 'transparent',
                  textDecoration: 'none',
                }}>
                <Icon size={17} strokeWidth={2} />
                {label}
              </Link>
            );
          })}
          <div style={{ borderTop: '1px solid var(--border)', marginTop: '0.5rem', paddingTop: '0.5rem' }}>
            <button onClick={handleLogout} style={{
              display: 'flex', alignItems: 'center', gap: '0.625rem',
              width: '100%', padding: '0.75rem 1rem', borderRadius: 8,
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: '0.9375rem', fontWeight: 500, color: 'var(--error)',
            }}>
              <LogOut size={17} strokeWidth={2} />
              Sign out
            </button>
          </div>
        </div>
      )}

      <style>{`
        @media (max-width: 640px) {
          .desktop-nav { display: none !important; }
          .mobile-menu-btn { display: flex !important; }
        }
      `}</style>
    </header>
  );
}
