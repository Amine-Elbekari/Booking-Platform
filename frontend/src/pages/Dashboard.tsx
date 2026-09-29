import { Search, Star, MapPin, Users, Wifi, Waves, ArrowRight, ChevronRight } from 'lucide-react';

// Demo villa data (no backend changes needed — placeholder cards that look real)
const VILLAS = [
  {
    id: 1,
    name: 'Villa Atlas',
    location: 'Marrakech, Morocco',
    price: 120,
    rating: 4.9,
    reviews: 148,
    guests: 8,
    image: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80',
    tag: 'Top rated',
    amenities: ['wifi', 'pool'],
  },
  {
    id: 2,
    name: 'Côte d\'Azur Suite',
    location: 'Nice, France',
    price: 280,
    rating: 4.8,
    reviews: 93,
    guests: 6,
    image: 'https://images.unsplash.com/photo-1499793983690-e29da59ef1c2?w=800&q=80',
    tag: 'Staff\'s pick',
    amenities: ['wifi', 'pool'],
  },
  {
    id: 3,
    name: 'Casa Bella',
    location: 'Tuscany, Italy',
    price: 195,
    rating: 4.95,
    reviews: 211,
    guests: 10,
    image: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
    tag: 'Superhost',
    amenities: ['wifi'],
  },
  {
    id: 4,
    name: 'Santorini Cliffs',
    location: 'Oia, Greece',
    price: 350,
    rating: 4.97,
    reviews: 76,
    guests: 4,
    image: 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?w=800&q=80',
    tag: 'New',
    amenities: ['wifi', 'pool'],
  },
  {
    id: 5,
    name: 'Bali Treehouse',
    location: 'Ubud, Indonesia',
    price: 89,
    rating: 4.85,
    reviews: 164,
    guests: 2,
    image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=800&q=80',
    tag: '',
    amenities: ['wifi'],
  },
  {
    id: 6,
    name: 'Algarve Retreat',
    location: 'Lagos, Portugal',
    price: 165,
    rating: 4.9,
    reviews: 102,
    guests: 6,
    image: 'https://images.unsplash.com/photo-1613553507747-5f8d62ad5904?w=800&q=80',
    tag: 'Popular',
    amenities: ['wifi', 'pool'],
  },
];

function VillaCard({ villa }: { villa: typeof VILLAS[0] }) {
  return (
    <article style={{
      background: 'var(--surface)',
      borderRadius: 'var(--radius-lg)',
      border: '1px solid var(--border)',
      overflow: 'hidden',
      transition: 'transform 0.2s ease, box-shadow 0.2s ease',
      cursor: 'pointer',
    }}
    onMouseEnter={e => {
      const el = e.currentTarget as HTMLElement;
      el.style.transform = 'translateY(-4px)';
      el.style.boxShadow = 'var(--shadow-lg)';
    }}
    onMouseLeave={e => {
      const el = e.currentTarget as HTMLElement;
      el.style.transform = 'translateY(0)';
      el.style.boxShadow = 'none';
    }}>
      {/* Image */}
      <div style={{ position: 'relative', height: 220, overflow: 'hidden' }}>
        <img
          src={villa.image}
          alt={villa.name}
          loading="lazy"
          style={{ width: '100%', height: '100%', objectFit: 'cover', transition: 'transform 0.4s ease' }}
          onMouseEnter={e => (e.currentTarget as HTMLElement).style.transform = 'scale(1.04)'}
          onMouseLeave={e => (e.currentTarget as HTMLElement).style.transform = 'scale(1)'}
        />
        {villa.tag && (
          <span style={{
            position: 'absolute', top: 12, left: 12,
            padding: '0.25rem 0.625rem',
            background: 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(4px)',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.75rem', fontWeight: 700,
            color: 'var(--accent)',
            boxShadow: 'var(--shadow-sm)',
          }}>{villa.tag}</span>
        )}
      </div>

      {/* Content */}
      <div style={{ padding: '1rem 1.25rem 1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.375rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>{villa.name}</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', flexShrink: 0 }}>
            <Star size={13} fill="#F59E0B" color="#F59E0B" />
            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-primary)' }}>{villa.rating}</span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>({villa.reviews})</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', marginBottom: '0.75rem' }}>
          <MapPin size={12} color="var(--text-muted)" strokeWidth={2} />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{villa.location}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <Users size={12} color="var(--text-muted)" strokeWidth={2} />
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Up to {villa.guests}</span>
          </div>
          {villa.amenities.includes('wifi') && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Wifi size={12} color="var(--text-muted)" strokeWidth={2} />
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>WiFi</span>
            </div>
          )}
          {villa.amenities.includes('pool') && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
              <Waves size={12} color="var(--text-muted)" strokeWidth={2} />
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Pool</span>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <span style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)' }}>€{villa.price}</span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}> / night</span>
          </div>
          <button className="btn btn-primary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            View villa <ArrowRight size={13} strokeWidth={2.5} />
          </button>
        </div>
      </div>
    </article>
  );
}

export default function Dashboard() {
  const hour = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening';

  return (
    <div style={{ background: 'var(--bg)', minHeight: 'calc(100vh - 64px)' }}>

      {/* Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, #1A0533 0%, #2D1065 60%, #4C1D95 100%)',
        padding: 'clamp(3rem, 6vw, 5rem) 1.5rem',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Decorative blobs */}
        <div style={{
          position: 'absolute', width: 400, height: 400,
          borderRadius: '50%', top: '-100px', right: '-80px',
          background: 'radial-gradient(circle, rgba(124,58,237,0.3) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />
        <div style={{
          position: 'absolute', width: 300, height: 300,
          borderRadius: '50%', bottom: '-80px', left: '-60px',
          background: 'radial-gradient(circle, rgba(192,132,252,0.2) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div style={{ position: 'relative', maxWidth: 720, margin: '0 auto' }}>
          <p style={{
            color: 'rgba(196,181,253,0.85)',
            fontSize: '0.875rem', fontWeight: 600, letterSpacing: '0.08em',
            textTransform: 'uppercase', marginBottom: '1rem',
          }}>
            {greeting} ✦
          </p>
          <h1 style={{
            color: '#fff',
            fontSize: 'clamp(2rem, 5vw, 3.25rem)',
            lineHeight: 1.15,
            marginBottom: '1.25rem',
            letterSpacing: '-0.03em',
          }}>
            Find your perfect<br />
            <span style={{ color: '#C084FC' }}>villa getaway</span>
          </h1>
          <p style={{
            color: 'rgba(255,255,255,0.65)',
            fontSize: '1.0625rem', marginBottom: '2.5rem',
          }}>
            Discover handpicked villas designed for unforgettable stays.
          </p>

          {/* Search bar */}
          <div style={{
            display: 'flex',
            background: 'rgba(255,255,255,0.95)',
            backdropFilter: 'blur(12px)',
            borderRadius: 14,
            boxShadow: '0 8px 32px rgba(0,0,0,0.25)',
            overflow: 'hidden',
            maxWidth: 640, margin: '0 auto',
          }}>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '0.625rem', padding: '0 1.25rem' }}>
              <Search size={16} color="var(--text-muted)" strokeWidth={2.5} />
              <input placeholder="Search destination, villa name..." style={{
                flex: 1, border: 'none', outline: 'none',
                fontFamily: 'Inter, sans-serif',
                fontSize: '0.9375rem',
                color: 'var(--text-primary)',
                background: 'transparent',
                padding: '1rem 0',
              }} />
            </div>
            <button className="btn btn-primary" style={{ borderRadius: 0, padding: '0 1.75rem', margin: '6px', borderRadius: 10 }}>
              Search
            </button>
          </div>

          {/* Quick filters */}
          <div style={{ display: 'flex', gap: '0.625rem', justifyContent: 'center', marginTop: '1.25rem', flexWrap: 'wrap' }}>
            {['Beachfront', 'Mountain views', 'Private pool', 'City center'].map(tag => (
              <button key={tag} style={{
                padding: '0.375rem 0.875rem',
                borderRadius: 'var(--radius-full)',
                border: '1px solid rgba(255,255,255,0.25)',
                background: 'rgba(255,255,255,0.12)',
                color: 'rgba(255,255,255,0.85)',
                fontSize: '0.8125rem', fontWeight: 500,
                cursor: 'pointer', transition: 'all 0.15s',
              }}
              onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.22)'}
              onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.12)'}>
                {tag}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Stats bar */}
      <section style={{
        borderBottom: '1px solid var(--border)',
        background: 'var(--surface)',
      }}>
        <div style={{
          maxWidth: 1280, margin: '0 auto',
          padding: '1rem 1.5rem',
          display: 'flex', gap: '2.5rem',
          overflowX: 'auto',
        }}>
          {[
            { label: 'Curated villas', value: '200+' },
            { label: 'Destinations', value: '48' },
            { label: 'Happy guests', value: '12k+' },
            { label: 'Avg. rating', value: '4.9 ★' },
          ].map(({ label, value }) => (
            <div key={label} style={{ flexShrink: 0 }}>
              <div style={{ fontWeight: 800, fontSize: '1.25rem', color: 'var(--accent)' }}>{value}</div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Villa grid */}
      <section style={{ maxWidth: 1280, margin: '0 auto', padding: '3rem 1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.75rem' }}>
          <div>
            <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Available villas</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{VILLAS.length} stays found</p>
          </div>
          <button className="btn btn-ghost" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.875rem' }}>
            View all <ChevronRight size={15} strokeWidth={2.5} />
          </button>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '1.5rem',
        }}>
          {VILLAS.map(villa => (
            <VillaCard key={villa.id} villa={villa} />
          ))}
        </div>
      </section>
    </div>
  );
}
