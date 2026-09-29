-- the btree_gist extension allow overlap exclusion constraint it's
-- a pure kernel lvl defense against double bookings
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- User TABLE

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    date_of_birth DATE,
    gender VARCHAR(20),
    address TEXT,
    country VARCHAR(20),
    city VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    asset_type VARCHAR NOT NULL,
    location VARCHAR(255) NOT NULL,
    price_per_night NUMERIC(10, 2) NOT NULL,
    max_guests INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE RESTRICT,

    -- Native range type for booking period
    -- The '[)' means inclusive of start date , exclusive of end date which is the checkout day
    booking_dates DATERANGE NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,

    adult_count INTEGER NOT NULL DEFAULT 1,
    child_count INTEGER NOT NULL DEFAULT 0,
    baby_count INTEGER NOT NULL DEFAULT 0,

    -- Status enforcement , so it will never be empty to track
    -- the current state of a reservation

    status VARCHAR(20) NOT NULL DEFAULT 'pending_payment',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- ! STRICT KERNEL CONSTRAINT !
    -- Ensure there is at least one adult or child per booking
    -- Note : CHECK can not be used for other tables
    CONSTRAINT valid_guest_count CHECK (adult_count + child_count >= 1),

    CONSTRAINT valid_status CHECK (status IN ('pending_payment', 'confirmed', 'cancelled', 'completed', 'expired')),

    -- The GiST Exclusion Constraint
    -- Exclude any new row where the asset_id is qual to an existing row,
    -- And the booking_dates overlap (&&) with an existing row.
    CONSTRAINT prevent_double_booking EXCLUDE USING gist (
        asset_id WITH =,
        booking_dates WITH &&
    ) WHERE (status != 'cancelled') -- ofc canneled booking don't block new ones
);

    -- Booking Guests to track all guests for one reservation
CREATE TABLE booking_guests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES  bookings(id) ON DELETE CASCADE,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    
    -- Type of guest based on age at the time of booking
    guest_type VARCHAR(20) NOT NULL,

    CONSTRAINT valid_guest_type CHECK (guest_type IN ('Adult', 'Child', 'Baby')) 
);

-- Indexes for fast lookups

CREATE INDEX idx_bookings_users ON bookings(user_id);
CREATE INDEX idx_bookings_guests_booking ON booking_guests(booking_id);
CREATE INDEX idx_bookings_availability ON bookings USING gist (asset_id, booking_dates);

-- Documents TABLE for RAG
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'UPLOADED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_document_status CHECK (status IN ('UPLOADED', 'EXTRACTING', 'CHUNKING', 'EMBEDDING', 'READY', 'FAILED'))
);

CREATE INDEX idx_documents_users ON documents(user_id);