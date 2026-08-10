package rest

import (
	"database/sql"

	"github.com/gin-gonic/gin"
	"github.com/kzkei/removeBeforeFlight/internal/app/handlers"
	"github.com/kzkei/removeBeforeFlight/internal/app/repos"
	"github.com/kzkei/removeBeforeFlight/internal/app/services"
)

// set up gin router and routes
func SetUpRouter(db *sql.DB) *gin.Engine {

	// init repo
	flightRepo := repos.NewFlightRepo(db)

	// init service
	flightService := services.NewFlightEmissionsService(flightRepo)

	// init handlers
	handlers := handlers.NewHandlers(flightService)

	// setup Gin router
	router := gin.Default()

	// setup routes
	router.GET("/health", handlers.HealthCheck)

	// api group
	apiGroup := router.Group("/api")

	{
		// flights group
		apiGroup.GET("/flights", handlers.GetFlights)                         // map
		apiGroup.GET("/flights/:icao/telemetry", handlers.GetFlightTelemetry) // single flight telemetry/emissions

		// emissions group
		apiGroup.GET("/emissions/circling", handlers.GetCirclingFlights)               // circling flights
		apiGroup.GET("/emissions/origincountry", handlers.GetEmissionsByOriginCountry) // registered origin country
		apiGroup.GET("/emissions/summary", handlers.GetEmissionsSummary)               // summary - main idea

	}

	return router
}
