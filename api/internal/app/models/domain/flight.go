package domain

type Flight struct {
	ICAOCode      string `json:"icao_code"`
	Callsign      string `json:"callsign"`
	OriginCoutnry string `json:"origin_country"`
}
