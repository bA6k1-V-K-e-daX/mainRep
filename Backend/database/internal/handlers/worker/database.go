package workhandler

import servicesdb "database/internal/services"

type Worker interface{}

type ServerAPI struct {
	database Worker
}

func SetWorker(s *servicesdb.WorkerService) *ServerAPI {
	return &ServerAPI{database: s}
}

func (s *ServerAPI) SetWorker() {
}
