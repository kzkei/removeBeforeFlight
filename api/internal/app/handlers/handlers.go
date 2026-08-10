package handlers

import (
	"log"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/kzkei/removeBeforeFlight/internal/app/models/response"
)

// interface for flight emissions service
type FlightEmissionsService interface {
	GetFlightTelemetry(flightICAO string) (*response.FlightResponse, error)
	GetFlights(limit int) ([]response.FlightResponse, error)
	GetEmissionsByOriginCountry(region, country string, limit int) ([]response.EmissionSummaryResponse, error)
	GetEmissionsSummary(limit int) ([]response.EmissionSummaryResponse, error)
	GetCirclingFlights() ([]response.FlightResponse, error)
}

type Handlers struct {
	flightEmissionsService FlightEmissionsService
}

func NewHandlers(
	flightEmissionsService FlightEmissionsService,
) *Handlers {
	return &Handlers{
		flightEmissionsService: flightEmissionsService,
	}
}

// Health check
func (h *Handlers) HealthCheck(c *gin.Context) {
	log.Println("HC hit")
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}

// single flight telemetry/emissions - used for singling out a flight to inspect its telemetry and estimated credits needed to offset its emissions
// api/flights/:icao/telemetry
func (h *Handlers) GetFlightTelemetry(c *gin.Context) {

	log.Println("GetFlightTelemetry hit")
	flightICAO := c.Param("icao")

	if flightICAO == "" || len(flightICAO) != 6 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "valid flight ICAO required"})
		return
	}

	// call service - check status

	// return status and data

}

// all flights - used for live flight map (include optional limit param)
func (h *Handlers) GetFlights(c *gin.Context) {
	log.Println("GetFlights hit")

	integer, err := strconv.Atoi(c.Query("limit"))
	if err != nil {
		log.Println("Error converting limit to int:", err)
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid limit parameter"})
		return
	}

	if integer < 0 || integer > 20000 {
		log.Println("Limit parameter out of range:", integer)
		c.JSON(http.StatusBadRequest, gin.H{"error": "limit parameter must be between 0 and 20000"})
		return
	}

	// call service - check status
}

// emissions by aircraft registered origin_country - get origin_country emissions, used for comparison (include optional limit param)
// includes active flights count
// /api/emissions/origincountry?limit=10
func (h *Handlers) GetEmissionsByOriginCountry(c *gin.Context) {

	log.Println("GetEmissionsByOriginCountry hit")

	// can be limited to specific origin_country or all
	// paramCountry := c.Query("origincountry")

	// validate params
}

// emissions summary - used for overall emissions summary dashboard (include optional limit param)
// /api/emissions/summary?limit=10
func (h *Handlers) GetEmissionsSummary(c *gin.Context) {

}

// for exposing identified holding patterns
func (h *Handlers) GetCirclingFlights(c *gin.Context) {

}
