package response

type FlightResponse struct {
	ICAOCode      string `json:"icao_code"`
	Callsign      string `json:"callsign"`
	OriginCountry string `json:"origin_country"`
}
