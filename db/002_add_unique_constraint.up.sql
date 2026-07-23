ALTER TABLE IF EXISTS raw_flight_states
ADD CONSTRAINT uniq_icao_last_contact UNIQUE (icao24, last_contact);