package config

import (
	"fmt"
	"log"
	"os"
	"path/filepath"

	"github.com/go-playground/validator/v10"
	"github.com/joho/godotenv"
)

type Config struct {
	DBHost     string `required:"true"`
	DBPort     string `required:"true"`
	DBUser     string `required:"true"`
	DBPassword string `required:"true"`
	DBName     string `required:"true"`
	APIPort    string `required:"true"`
}

// load .env file and return a Config struct
func LoadConfig() (*Config, error) {

	log.Printf("loading config environment vars")
	// find and load dotenv from parent directory
	envPath := filepath.Join("..", ".env")

	err := godotenv.Load(envPath)
	if err != nil {
		return nil, fmt.Errorf("error loading .env file: %v", err)
	}

	config := &Config{
		DBHost:     os.Getenv("DB_HOST"),
		DBPort:     os.Getenv("DB_PORT"),
		DBUser:     os.Getenv("DB_USER"),
		DBPassword: os.Getenv("DB_PASSWORD"),
		DBName:     os.Getenv("DB_NAME"),
		APIPort:    os.Getenv("API_PORT"),
	}

	// validate config struct
	v := validator.New()
	err = v.Struct(config)
	if err != nil {
		return nil, fmt.Errorf("error validating config: %v", err)
	}

	return config, err
}

// return the connection string
func (c *Config) GetDSN() string {
	return fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		c.DBHost,
		c.DBPort,
		c.DBUser,
		c.DBPassword,
		c.DBName)
}
