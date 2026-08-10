package response

type EmissionSummaryResponse struct {
	Flights []FlightResponse `json:"flights"`
}
