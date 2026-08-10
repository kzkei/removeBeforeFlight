package repos

import (
	"database/sql"

	"github.com/kzkei/removeBeforeFlight/internal/app/models/response"
)

type FlightRepo struct {
	db *sql.DB
}

func NewFlightRepo(db *sql.DB) *FlightRepo {
	return &FlightRepo{
		db: db,
	}
}

func (r *FlightRepo) GetFlightTelemetry(flightICAO string) (*response.FlightResponse, error) {
	return nil, nil
}

func (r *FlightRepo) GetFlights(limit int) ([]response.FlightResponse, error) {
	return nil, nil
}

func (r *FlightRepo) GetEmissionsByOriginCountry(country string, limit int) ([]response.EmissionSummaryResponse, error) {
	return nil, nil
}

func (r *FlightRepo) GetEmissionsSummary(limit int) ([]response.EmissionSummaryResponse, error) {
	return nil, nil
}

func (r *FlightRepo) GetCirclingFlights() ([]response.FlightResponse, error) {
	return nil, nil
}
