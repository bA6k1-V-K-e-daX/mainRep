package servicesdb

import dbrepo "database/internal/repository"

type Database struct{}

type WorkerService struct{}

func New(db *dbrepo.DatabaseRepo) (*Database, *WorkerService) {
	return &Database{}, &WorkerService{}
}
