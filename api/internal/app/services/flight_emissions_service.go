package services

import "github.com/kzkei/removeBeforeFlight/internal/app/models/response"

type FlightRepo interface {
	// Methods that the flight repository implements
	GetFlightTelemetry(flightICAO string) (*response.FlightResponse, error)
	GetFlights(limit int) ([]response.FlightResponse, error)
	GetEmissionsByOriginCountry(country string, limit int) ([]response.EmissionSummaryResponse, error)
	GetEmissionsSummary(limit int) ([]response.EmissionSummaryResponse, error)
	GetCirclingFlights() ([]response.FlightResponse, error)
}

type FlightEmissionsService struct {
	flightRepo FlightRepo
}

func NewFlightEmissionsService(flightRepo FlightRepo) *FlightEmissionsService {
	return &FlightEmissionsService{
		flightRepo: flightRepo,
	}
}

func (s *FlightEmissionsService) GetFlightTelemetry(flightICAO string) (*response.FlightResponse, error) {
	return s.flightRepo.GetFlightTelemetry(flightICAO)
}

func (s *FlightEmissionsService) GetFlights(limit int) ([]response.FlightResponse, error) {
	return s.flightRepo.GetFlights(limit)
}

func (s *FlightEmissionsService) GetEmissionsByOriginCountry(region, country string, limit int) ([]response.EmissionSummaryResponse, error) {
	return s.flightRepo.GetEmissionsByOriginCountry(country, limit)
}

func (s *FlightEmissionsService) GetEmissionsSummary(limit int) ([]response.EmissionSummaryResponse, error) {
	return s.flightRepo.GetEmissionsSummary(limit)
}

func (s *FlightEmissionsService) GetCirclingFlights() ([]response.FlightResponse, error) {
	return s.flightRepo.GetCirclingFlights()
}
