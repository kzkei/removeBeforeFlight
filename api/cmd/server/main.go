package cmd

import (
	"database/sql"
	"log"

	"github.com/kzkei/removeBeforeFlight/internal/config"
	"github.com/kzkei/removeBeforeFlight/internal/rest"
)

func main() {

	// load config
	config, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
		return
	}

	// open db connection with pgx driver
	db, err := sql.Open("pgx", config.GetDSN())
	if err != nil {
		log.Fatalf("Error connecting to database: %v", err)
		return
	}

	// ping
	if err := db.Ping(); err != nil {
		log.Fatalf("Error pinging database: %v", err)
		return
	}

	// set up router
	router := rest.SetUpRouter(db)

	// run server
	if err := router.Run(":" + config.APIPort); err != nil {
		log.Fatalf("Error starting server: %v", err)
		return
	}
}
