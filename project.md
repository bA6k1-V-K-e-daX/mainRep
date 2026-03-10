### DIRECTORY . FOLDER STRUCTURE ###
DIR Backend/
    DIR database/
        DIR cmd/
            FILE main.go
        DIR config/
            FILE config.yaml
        DIR contract/
            FILE database.pb.go
            FILE database_grpc.pb.go
        FILE Dockerfile
        FILE go.mod
        FILE go.sum
        DIR internal/
            DIR app/
                FILE app.go
                DIR grpc/
                    FILE app.go
            DIR config/
                FILE config.go
            DIR handlers/
                DIR grpc/
                    FILE server.go
            DIR migrations/
                FILE 1_init_schema.down.sql
                FILE 1_init_schema.up.sql
            DIR migrator/
                FILE migrator.go
            DIR models/
                FILE models.go
            DIR repository/
                FILE database.go
            DIR services/
                FILE database.go
    DIR manager/
        DIR cmd/
            FILE main.go
        DIR config/
            FILE config.yaml
        DIR contract/
            DIR database/
                FILE database.pb.go
                FILE database_grpc.pb.go
            DIR ml/
                FILE ml.pb.go
                FILE ml_grpc.pb.go
        FILE Dockerfile
        FILE go.mod
        FILE go.sum
        DIR internal/
            DIR app/
                FILE app.go
                DIR http/
                    FILE app.go
            DIR config/
                FILE config.go
            DIR models/
                FILE models.go
            DIR repository/
                DIR database/
                    FILE client.go
                DIR ml/
                    FILE client.go
            DIR router/
                FILE router.go
            DIR services/
                FILE http.go
            DIR volume/
    DIR test/
        FILE e2e.go
        FILE go.mod
        DIR testdata/
            FILE test1.jpg
            FILE test2.jpg
FILE docker-compose.yaml
DIR Frontend/
    DIR popki-first/
        FILE .gitignore
        FILE eslint.config.js
        FILE index.html
        FILE package-lock.json
        FILE package.json
        DIR public/
            FILE razminirovanie.png
            FILE Rectangle_10.png
            FILE Rectangle_11.png
            FILE Rectangle_12.png
            FILE Rectangle_13.png
            FILE Rectangle_15.png
        FILE README.md
        DIR src/
            FILE App.css
            FILE App.jsx
            DIR Components/
                FILE About.jsx
                FILE Button.jsx
                FILE Faqs.jsx
                FILE Greeting.jsx
                FILE Header.jsx
                FILE Rights.jsx
                FILE TryPeeky.jsx
                FILE Yolo.jsx
            FILE index.css
            FILE main.jsx
            DIR Pages/
                FILE Auth.jsx
                FILE GreetingsPage.jsx
                FILE Registration.jsx
        FILE vite.config.js
DIR ML/
    FILE .gitignore
    DIR app/
        DIR core/
            FILE coco_classes.py
            FILE di_container.py
        DIR grps/
            DIR protos/
                FILE detector.proto
                FILE detector_pb2.py
                FILE detector_pb2_grpc.py
                FILE __init__.py
            FILE server.py
            FILE __init__.py
        DIR scenaries/
            FILE detect_batch_image.py
            FILE detect_image.py
            FILE detect_video.py
        DIR scripts/
            FILE download_model.py
            FILE start_upload_container.bat
            FILE upload_container_images.ps1
        DIR services/
            FILE model_loader.py
            FILE __init__.py
        DIR utils/
            FILE generate_report.py
            FILE names_to_ids.py
            FILE __init__.py
    FILE dockerfile
    FILE main.py
    FILE README.md
    FILE requirements.txt
    FILE test_client.py
FILE project.md
FILE README.md
### DIRECTORY . FOLDER STRUCTURE ###

### DIRECTORY . FLATTENED CONTENT ###
### .\Backend\database\cmd\main.go BEGIN ###
package main

import (
	"database/internal/app"
	"database/internal/config"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
)

func main() {
	config, level := config.MustLoad()
	err := logger.Init(level, config.Env, config.FilePath)
	if err != nil {
		fmt.Printf("Failed to init logger: %v\n", err)
		return
	}
	defer func() {
		if err := logger.Close(); err != nil {
			fmt.Printf("Failed to close logger: %v\n", err)
		}
	}()
	logger.Info("Config has been successfully loaded", nil)
	logger.Debug("Config data", 1000, map[string]any{
		"env":                      config.Env,
		"format_time":              config.FormatTime,
		"file_path":                config.FilePath,
		"grpc_port":                config.GRPC.Port,
		"grpc_timeout":             config.GRPC.Timeout,
		"database_port":            config.Database.Port,
		"database_host":            config.Database.Host,
		"database_user":            config.Database.User,
		"database_database":        config.Database.Database,
		"database_migrations_path": config.Database.MigrationsPath,
	})
	application := app.New(config.Database, config.GRPC.Port)
	logger.Info("Application has been successfully initialized", nil)
	go func() {
		application.GRPCServer.MustRun()
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop
	application.GRPCServer.Stop()
	logger.Info("Gracefully stopped", nil)
}

### .\Backend\database\cmd\main.go END ###

### .\Backend\database\config\config.yaml BEGIN ###
env: "local" # debug, local, test, production
format_time: "RFC3339"
file_path: "app.log"

grpc:
  port: 2021
  timeout: 20

postgres:
  host: "db"
  port: 5432
  user: "babkivkedah"
  password: "tapki.com"
  database: "projectml"
  migrations_path: "file://migrations"
### .\Backend\database\config\config.yaml END ###

### .\Backend\database\contract\database.pb.go BEGIN ###
// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.36.10
// 	protoc        v6.33.1
// source: newp/database/database.proto

package database1

import (
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
	unsafe "unsafe"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type CreateUserRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CreateUserRequest) Reset() {
	*x = CreateUserRequest{}
	mi := &file_newp_database_database_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CreateUserRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CreateUserRequest) ProtoMessage() {}

func (x *CreateUserRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CreateUserRequest.ProtoReflect.Descriptor instead.
func (*CreateUserRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{0}
}

func (x *CreateUserRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *CreateUserRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type CreateUserResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CreateUserResponse) Reset() {
	*x = CreateUserResponse{}
	mi := &file_newp_database_database_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CreateUserResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CreateUserResponse) ProtoMessage() {}

func (x *CreateUserResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CreateUserResponse.ProtoReflect.Descriptor instead.
func (*CreateUserResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{1}
}

func (x *CreateUserResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

type CheckUserRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CheckUserRequest) Reset() {
	*x = CheckUserRequest{}
	mi := &file_newp_database_database_proto_msgTypes[2]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CheckUserRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CheckUserRequest) ProtoMessage() {}

func (x *CheckUserRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[2]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CheckUserRequest.ProtoReflect.Descriptor instead.
func (*CheckUserRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{2}
}

func (x *CheckUserRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *CheckUserRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type CheckUserResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CheckUserResponse) Reset() {
	*x = CheckUserResponse{}
	mi := &file_newp_database_database_proto_msgTypes[3]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CheckUserResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CheckUserResponse) ProtoMessage() {}

func (x *CheckUserResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[3]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CheckUserResponse.ProtoReflect.Descriptor instead.
func (*CheckUserResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{3}
}

func (x *CheckUserResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

func (x *CheckUserResponse) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type DeleteUserRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *DeleteUserRequest) Reset() {
	*x = DeleteUserRequest{}
	mi := &file_newp_database_database_proto_msgTypes[4]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *DeleteUserRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*DeleteUserRequest) ProtoMessage() {}

func (x *DeleteUserRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[4]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use DeleteUserRequest.ProtoReflect.Descriptor instead.
func (*DeleteUserRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{4}
}

func (x *DeleteUserRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *DeleteUserRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type DeleteUserResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *DeleteUserResponse) Reset() {
	*x = DeleteUserResponse{}
	mi := &file_newp_database_database_proto_msgTypes[5]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *DeleteUserResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*DeleteUserResponse) ProtoMessage() {}

func (x *DeleteUserResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[5]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use DeleteUserResponse.ProtoReflect.Descriptor instead.
func (*DeleteUserResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{5}
}

func (x *DeleteUserResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

type AddNewAnswerRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *AddNewAnswerRequest) Reset() {
	*x = AddNewAnswerRequest{}
	mi := &file_newp_database_database_proto_msgTypes[6]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *AddNewAnswerRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*AddNewAnswerRequest) ProtoMessage() {}

func (x *AddNewAnswerRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[6]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use AddNewAnswerRequest.ProtoReflect.Descriptor instead.
func (*AddNewAnswerRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{6}
}

func (x *AddNewAnswerRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *AddNewAnswerRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type AddNewAnswerResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *AddNewAnswerResponse) Reset() {
	*x = AddNewAnswerResponse{}
	mi := &file_newp_database_database_proto_msgTypes[7]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *AddNewAnswerResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*AddNewAnswerResponse) ProtoMessage() {}

func (x *AddNewAnswerResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[7]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use AddNewAnswerResponse.ProtoReflect.Descriptor instead.
func (*AddNewAnswerResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{7}
}

func (x *AddNewAnswerResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

type RequestOldAnswersRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Quantity      int64                  `protobuf:"varint,1,opt,name=Quantity,proto3" json:"Quantity,omitempty"`
	Flag          string                 `protobuf:"bytes,2,opt,name=Flag,proto3" json:"Flag,omitempty"`
	UserID        string                 `protobuf:"bytes,3,opt,name=UserID,proto3" json:"UserID,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestOldAnswersRequest) Reset() {
	*x = RequestOldAnswersRequest{}
	mi := &file_newp_database_database_proto_msgTypes[8]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestOldAnswersRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestOldAnswersRequest) ProtoMessage() {}

func (x *RequestOldAnswersRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[8]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestOldAnswersRequest.ProtoReflect.Descriptor instead.
func (*RequestOldAnswersRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{8}
}

func (x *RequestOldAnswersRequest) GetQuantity() int64 {
	if x != nil {
		return x.Quantity
	}
	return 0
}

func (x *RequestOldAnswersRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *RequestOldAnswersRequest) GetUserID() string {
	if x != nil {
		return x.UserID
	}
	return ""
}

type RequestOldAnswersResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestOldAnswersResponse) Reset() {
	*x = RequestOldAnswersResponse{}
	mi := &file_newp_database_database_proto_msgTypes[9]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestOldAnswersResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestOldAnswersResponse) ProtoMessage() {}

func (x *RequestOldAnswersResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[9]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestOldAnswersResponse.ProtoReflect.Descriptor instead.
func (*RequestOldAnswersResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{9}
}

func (x *RequestOldAnswersResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

func (x *RequestOldAnswersResponse) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type RequestDeletedAnswersRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	UserID        string                 `protobuf:"bytes,2,opt,name=UserID,proto3" json:"UserID,omitempty"`
	Data          []byte                 `protobuf:"bytes,3,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestDeletedAnswersRequest) Reset() {
	*x = RequestDeletedAnswersRequest{}
	mi := &file_newp_database_database_proto_msgTypes[10]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestDeletedAnswersRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestDeletedAnswersRequest) ProtoMessage() {}

func (x *RequestDeletedAnswersRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[10]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestDeletedAnswersRequest.ProtoReflect.Descriptor instead.
func (*RequestDeletedAnswersRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{10}
}

func (x *RequestDeletedAnswersRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *RequestDeletedAnswersRequest) GetUserID() string {
	if x != nil {
		return x.UserID
	}
	return ""
}

func (x *RequestDeletedAnswersRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type RequestDeletedAnswersResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestDeletedAnswersResponse) Reset() {
	*x = RequestDeletedAnswersResponse{}
	mi := &file_newp_database_database_proto_msgTypes[11]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestDeletedAnswersResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestDeletedAnswersResponse) ProtoMessage() {}

func (x *RequestDeletedAnswersResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[11]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestDeletedAnswersResponse.ProtoReflect.Descriptor instead.
func (*RequestDeletedAnswersResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{11}
}

func (x *RequestDeletedAnswersResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

var File_newp_database_database_proto protoreflect.FileDescriptor

const file_newp_database_database_proto_rawDesc = "" +
	"\n" +
	"\x1cnewp/database/database.proto\x12\bdatabase\";\n" +
	"\x11CreateUserRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\".\n" +
	"\x12CreateUserResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\":\n" +
	"\x10CheckUserRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\"A\n" +
	"\x11CheckUserResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\";\n" +
	"\x11DeleteUserRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\".\n" +
	"\x12DeleteUserResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\"=\n" +
	"\x13AddNewAnswerRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\"0\n" +
	"\x14AddNewAnswerResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\"b\n" +
	"\x18RequestOldAnswersRequest\x12\x1a\n" +
	"\bQuantity\x18\x01 \x01(\x03R\bQuantity\x12\x12\n" +
	"\x04Flag\x18\x02 \x01(\tR\x04Flag\x12\x16\n" +
	"\x06UserID\x18\x03 \x01(\tR\x06UserID\"I\n" +
	"\x19RequestOldAnswersResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\"^\n" +
	"\x1cRequestDeletedAnswersRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x16\n" +
	"\x06UserID\x18\x02 \x01(\tR\x06UserID\x12\x12\n" +
	"\x04Data\x18\x03 \x01(\fR\x04Data\"9\n" +
	"\x1dRequestDeletedAnswersResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage2\xf3\x03\n" +
	"\bDatabase\x12G\n" +
	"\n" +
	"CreateUser\x12\x1b.database.CreateUserRequest\x1a\x1c.database.CreateUserResponse\x12D\n" +
	"\tCheckUser\x12\x1a.database.CheckUserRequest\x1a\x1b.database.CheckUserResponse\x12G\n" +
	"\n" +
	"DeleteUser\x12\x1b.database.DeleteUserRequest\x1a\x1c.database.DeleteUserResponse\x12K\n" +
	"\n" +
	"AddNewData\x12\x1d.database.AddNewAnswerRequest\x1a\x1e.database.AddNewAnswerResponse\x12Z\n" +
	"\x0fRequestOldDatas\x12\".database.RequestOldAnswersRequest\x1a#.database.RequestOldAnswersResponse\x12f\n" +
	"\x13RequestDeletedDatas\x12&.database.RequestDeletedAnswersRequest\x1a'.database.RequestDeletedAnswersResponseB\x1eZ\x1csirius.database.v1;database1b\x06proto3"

var (
	file_newp_database_database_proto_rawDescOnce sync.Once
	file_newp_database_database_proto_rawDescData []byte
)

func file_newp_database_database_proto_rawDescGZIP() []byte {
	file_newp_database_database_proto_rawDescOnce.Do(func() {
		file_newp_database_database_proto_rawDescData = protoimpl.X.CompressGZIP(unsafe.Slice(unsafe.StringData(file_newp_database_database_proto_rawDesc), len(file_newp_database_database_proto_rawDesc)))
	})
	return file_newp_database_database_proto_rawDescData
}

var file_newp_database_database_proto_msgTypes = make([]protoimpl.MessageInfo, 12)
var file_newp_database_database_proto_goTypes = []any{
	(*CreateUserRequest)(nil),             // 0: database.CreateUserRequest
	(*CreateUserResponse)(nil),            // 1: database.CreateUserResponse
	(*CheckUserRequest)(nil),              // 2: database.CheckUserRequest
	(*CheckUserResponse)(nil),             // 3: database.CheckUserResponse
	(*DeleteUserRequest)(nil),             // 4: database.DeleteUserRequest
	(*DeleteUserResponse)(nil),            // 5: database.DeleteUserResponse
	(*AddNewAnswerRequest)(nil),           // 6: database.AddNewAnswerRequest
	(*AddNewAnswerResponse)(nil),          // 7: database.AddNewAnswerResponse
	(*RequestOldAnswersRequest)(nil),      // 8: database.RequestOldAnswersRequest
	(*RequestOldAnswersResponse)(nil),     // 9: database.RequestOldAnswersResponse
	(*RequestDeletedAnswersRequest)(nil),  // 10: database.RequestDeletedAnswersRequest
	(*RequestDeletedAnswersResponse)(nil), // 11: database.RequestDeletedAnswersResponse
}
var file_newp_database_database_proto_depIdxs = []int32{
	0,  // 0: database.Database.CreateUser:input_type -> database.CreateUserRequest
	2,  // 1: database.Database.CheckUser:input_type -> database.CheckUserRequest
	4,  // 2: database.Database.DeleteUser:input_type -> database.DeleteUserRequest
	6,  // 3: database.Database.AddNewData:input_type -> database.AddNewAnswerRequest
	8,  // 4: database.Database.RequestOldDatas:input_type -> database.RequestOldAnswersRequest
	10, // 5: database.Database.RequestDeletedDatas:input_type -> database.RequestDeletedAnswersRequest
	1,  // 6: database.Database.CreateUser:output_type -> database.CreateUserResponse
	3,  // 7: database.Database.CheckUser:output_type -> database.CheckUserResponse
	5,  // 8: database.Database.DeleteUser:output_type -> database.DeleteUserResponse
	7,  // 9: database.Database.AddNewData:output_type -> database.AddNewAnswerResponse
	9,  // 10: database.Database.RequestOldDatas:output_type -> database.RequestOldAnswersResponse
	11, // 11: database.Database.RequestDeletedDatas:output_type -> database.RequestDeletedAnswersResponse
	6,  // [6:12] is the sub-list for method output_type
	0,  // [0:6] is the sub-list for method input_type
	0,  // [0:0] is the sub-list for extension type_name
	0,  // [0:0] is the sub-list for extension extendee
	0,  // [0:0] is the sub-list for field type_name
}

func init() { file_newp_database_database_proto_init() }
func file_newp_database_database_proto_init() {
	if File_newp_database_database_proto != nil {
		return
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: unsafe.Slice(unsafe.StringData(file_newp_database_database_proto_rawDesc), len(file_newp_database_database_proto_rawDesc)),
			NumEnums:      0,
			NumMessages:   12,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_newp_database_database_proto_goTypes,
		DependencyIndexes: file_newp_database_database_proto_depIdxs,
		MessageInfos:      file_newp_database_database_proto_msgTypes,
	}.Build()
	File_newp_database_database_proto = out.File
	file_newp_database_database_proto_goTypes = nil
	file_newp_database_database_proto_depIdxs = nil
}

### .\Backend\database\contract\database.pb.go END ###

### .\Backend\database\contract\database_grpc.pb.go BEGIN ###
// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.5.1
// - protoc             v6.33.1
// source: newp/database/database.proto

package database1

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.64.0 or later.
const _ = grpc.SupportPackageIsVersion9

const (
	Database_CreateUser_FullMethodName          = "/database.Database/CreateUser"
	Database_CheckUser_FullMethodName           = "/database.Database/CheckUser"
	Database_DeleteUser_FullMethodName          = "/database.Database/DeleteUser"
	Database_AddNewData_FullMethodName          = "/database.Database/AddNewData"
	Database_RequestOldDatas_FullMethodName     = "/database.Database/RequestOldDatas"
	Database_RequestDeletedDatas_FullMethodName = "/database.Database/RequestDeletedDatas"
)

// DatabaseClient is the client API for Database service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type DatabaseClient interface {
	CreateUser(ctx context.Context, in *CreateUserRequest, opts ...grpc.CallOption) (*CreateUserResponse, error)
	CheckUser(ctx context.Context, in *CheckUserRequest, opts ...grpc.CallOption) (*CheckUserResponse, error)
	DeleteUser(ctx context.Context, in *DeleteUserRequest, opts ...grpc.CallOption) (*DeleteUserResponse, error)
	AddNewData(ctx context.Context, in *AddNewAnswerRequest, opts ...grpc.CallOption) (*AddNewAnswerResponse, error)
	RequestOldDatas(ctx context.Context, in *RequestOldAnswersRequest, opts ...grpc.CallOption) (*RequestOldAnswersResponse, error)
	RequestDeletedDatas(ctx context.Context, in *RequestDeletedAnswersRequest, opts ...grpc.CallOption) (*RequestDeletedAnswersResponse, error)
}

type databaseClient struct {
	cc grpc.ClientConnInterface
}

func NewDatabaseClient(cc grpc.ClientConnInterface) DatabaseClient {
	return &databaseClient{cc}
}

func (c *databaseClient) CreateUser(ctx context.Context, in *CreateUserRequest, opts ...grpc.CallOption) (*CreateUserResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(CreateUserResponse)
	err := c.cc.Invoke(ctx, Database_CreateUser_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) CheckUser(ctx context.Context, in *CheckUserRequest, opts ...grpc.CallOption) (*CheckUserResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(CheckUserResponse)
	err := c.cc.Invoke(ctx, Database_CheckUser_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) DeleteUser(ctx context.Context, in *DeleteUserRequest, opts ...grpc.CallOption) (*DeleteUserResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(DeleteUserResponse)
	err := c.cc.Invoke(ctx, Database_DeleteUser_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) AddNewData(ctx context.Context, in *AddNewAnswerRequest, opts ...grpc.CallOption) (*AddNewAnswerResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(AddNewAnswerResponse)
	err := c.cc.Invoke(ctx, Database_AddNewData_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) RequestOldDatas(ctx context.Context, in *RequestOldAnswersRequest, opts ...grpc.CallOption) (*RequestOldAnswersResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(RequestOldAnswersResponse)
	err := c.cc.Invoke(ctx, Database_RequestOldDatas_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) RequestDeletedDatas(ctx context.Context, in *RequestDeletedAnswersRequest, opts ...grpc.CallOption) (*RequestDeletedAnswersResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(RequestDeletedAnswersResponse)
	err := c.cc.Invoke(ctx, Database_RequestDeletedDatas_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// DatabaseServer is the server API for Database service.
// All implementations must embed UnimplementedDatabaseServer
// for forward compatibility.
type DatabaseServer interface {
	CreateUser(context.Context, *CreateUserRequest) (*CreateUserResponse, error)
	CheckUser(context.Context, *CheckUserRequest) (*CheckUserResponse, error)
	DeleteUser(context.Context, *DeleteUserRequest) (*DeleteUserResponse, error)
	AddNewData(context.Context, *AddNewAnswerRequest) (*AddNewAnswerResponse, error)
	RequestOldDatas(context.Context, *RequestOldAnswersRequest) (*RequestOldAnswersResponse, error)
	RequestDeletedDatas(context.Context, *RequestDeletedAnswersRequest) (*RequestDeletedAnswersResponse, error)
	mustEmbedUnimplementedDatabaseServer()
}

// UnimplementedDatabaseServer must be embedded to have
// forward compatible implementations.
//
// NOTE: this should be embedded by value instead of pointer to avoid a nil
// pointer dereference when methods are called.
type UnimplementedDatabaseServer struct{}

func (UnimplementedDatabaseServer) CreateUser(context.Context, *CreateUserRequest) (*CreateUserResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method CreateUser not implemented")
}
func (UnimplementedDatabaseServer) CheckUser(context.Context, *CheckUserRequest) (*CheckUserResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method CheckUser not implemented")
}
func (UnimplementedDatabaseServer) DeleteUser(context.Context, *DeleteUserRequest) (*DeleteUserResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method DeleteUser not implemented")
}
func (UnimplementedDatabaseServer) AddNewData(context.Context, *AddNewAnswerRequest) (*AddNewAnswerResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method AddNewData not implemented")
}
func (UnimplementedDatabaseServer) RequestOldDatas(context.Context, *RequestOldAnswersRequest) (*RequestOldAnswersResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RequestOldDatas not implemented")
}
func (UnimplementedDatabaseServer) RequestDeletedDatas(context.Context, *RequestDeletedAnswersRequest) (*RequestDeletedAnswersResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RequestDeletedDatas not implemented")
}
func (UnimplementedDatabaseServer) mustEmbedUnimplementedDatabaseServer() {}
func (UnimplementedDatabaseServer) testEmbeddedByValue()                  {}

// UnsafeDatabaseServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to DatabaseServer will
// result in compilation errors.
type UnsafeDatabaseServer interface {
	mustEmbedUnimplementedDatabaseServer()
}

func RegisterDatabaseServer(s grpc.ServiceRegistrar, srv DatabaseServer) {
	// If the following call pancis, it indicates UnimplementedDatabaseServer was
	// embedded by pointer and is nil.  This will cause panics if an
	// unimplemented method is ever invoked, so we test this at initialization
	// time to prevent it from happening at runtime later due to I/O.
	if t, ok := srv.(interface{ testEmbeddedByValue() }); ok {
		t.testEmbeddedByValue()
	}
	s.RegisterService(&Database_ServiceDesc, srv)
}

func _Database_CreateUser_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(CreateUserRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).CreateUser(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_CreateUser_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).CreateUser(ctx, req.(*CreateUserRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_CheckUser_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(CheckUserRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).CheckUser(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_CheckUser_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).CheckUser(ctx, req.(*CheckUserRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_DeleteUser_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DeleteUserRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).DeleteUser(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_DeleteUser_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).DeleteUser(ctx, req.(*DeleteUserRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_AddNewData_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(AddNewAnswerRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).AddNewData(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_AddNewData_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).AddNewData(ctx, req.(*AddNewAnswerRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_RequestOldDatas_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(RequestOldAnswersRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).RequestOldDatas(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_RequestOldDatas_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).RequestOldDatas(ctx, req.(*RequestOldAnswersRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_RequestDeletedDatas_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(RequestDeletedAnswersRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).RequestDeletedDatas(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_RequestDeletedDatas_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).RequestDeletedDatas(ctx, req.(*RequestDeletedAnswersRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// Database_ServiceDesc is the grpc.ServiceDesc for Database service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var Database_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "database.Database",
	HandlerType: (*DatabaseServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "CreateUser",
			Handler:    _Database_CreateUser_Handler,
		},
		{
			MethodName: "CheckUser",
			Handler:    _Database_CheckUser_Handler,
		},
		{
			MethodName: "DeleteUser",
			Handler:    _Database_DeleteUser_Handler,
		},
		{
			MethodName: "AddNewData",
			Handler:    _Database_AddNewData_Handler,
		},
		{
			MethodName: "RequestOldDatas",
			Handler:    _Database_RequestOldDatas_Handler,
		},
		{
			MethodName: "RequestDeletedDatas",
			Handler:    _Database_RequestDeletedDatas_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "newp/database/database.proto",
}

### .\Backend\database\contract\database_grpc.pb.go END ###

### .\Backend\database\Dockerfile BEGIN ###
FROM golang:1.24-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o /database ./cmd/main.go

FROM alpine:latest

WORKDIR /app

COPY --from=builder /database .
COPY config/ config/
COPY internal/migrations/ migrations/

EXPOSE 2021

CMD ["./database", "--config=config/config.yaml"]

### .\Backend\database\Dockerfile END ###

### .\Backend\database\go.mod BEGIN ###
module database

go 1.24.2

require (
	github.com/PrototypeSirius/ruglogger v0.0.0-20260124155947-d30e99226478
	github.com/golang-migrate/migrate/v4 v4.19.1
	github.com/ilyakaznacheev/cleanenv v1.5.0
	github.com/lib/pq v1.10.9
	google.golang.org/grpc v1.79.1
	google.golang.org/protobuf v1.36.11
)

require (
	github.com/BurntSushi/toml v1.2.1 // indirect
	github.com/joho/godotenv v1.5.1 // indirect
	golang.org/x/net v0.48.0 // indirect
	golang.org/x/sys v0.39.0 // indirect
	golang.org/x/text v0.32.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
	olympos.io/encoding/edn v0.0.0-20201019073823-d3554ca0b0a3 // indirect
)

### .\Backend\database\go.mod END ###

### .\Backend\database\go.sum BEGIN ###
github.com/Azure/go-ansiterm v0.0.0-20230124172434-306776ec8161 h1:L/gRVlceqvL25UVaW/CKtUDjefjrs0SPonmDGUVOYP0=
github.com/Azure/go-ansiterm v0.0.0-20230124172434-306776ec8161/go.mod h1:xomTg63KZ2rFqZQzSB4Vz2SUXa1BpHTVz9L5PTmPC4E=
github.com/BurntSushi/toml v1.2.1 h1:9F2/+DoOYIOksmaJFPw1tGFy1eDnIJXg+UHjuD8lTak=
github.com/BurntSushi/toml v1.2.1/go.mod h1:CxXYINrC8qIiEnFrOxCa7Jy5BFHlXnUU2pbicEuybxQ=
github.com/Microsoft/go-winio v0.6.2 h1:F2VQgta7ecxGYO8k3ZZz3RS8fVIXVxONVUPlNERoyfY=
github.com/Microsoft/go-winio v0.6.2/go.mod h1:yd8OoFMLzJbo9gZq8j5qaps8bJ9aShtEA8Ipt1oGCvU=
github.com/PrototypeSirius/ruglogger v0.0.0-20260124155947-d30e99226478 h1:1saj4+qX1UccPw6ZKB4FVG+uzGm47OTGHur6ohLbGFo=
github.com/PrototypeSirius/ruglogger v0.0.0-20260124155947-d30e99226478/go.mod h1:Gpp4OyX1d/1u7csaTbgA7OArFj/AfIoBFntLeb3VCY8=
github.com/cespare/xxhash/v2 v2.3.0 h1:UL815xU9SqsFlibzuggzjXhog7bL6oX9BbNZnL2UFvs=
github.com/cespare/xxhash/v2 v2.3.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
github.com/containerd/errdefs v1.0.0 h1:tg5yIfIlQIrxYtu9ajqY42W3lpS19XqdxRQeEwYG8PI=
github.com/containerd/errdefs v1.0.0/go.mod h1:+YBYIdtsnF4Iw6nWZhJcqGSg/dwvV7tyJ/kCkyJ2k+M=
github.com/containerd/errdefs/pkg v0.3.0 h1:9IKJ06FvyNlexW690DXuQNx2KA2cUJXx151Xdx3ZPPE=
github.com/containerd/errdefs/pkg v0.3.0/go.mod h1:NJw6s9HwNuRhnjJhM7pylWwMyAkmCQvQ4GpJHEqRLVk=
github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc h1:U9qPSI2PIWSS1VwoXQT9A3Wy9MM3WgvqSxFWenqJduM=
github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/dhui/dktest v0.4.6 h1:+DPKyScKSEp3VLtbMDHcUq6V5Lm5zfZZVb0Sk7Ahom4=
github.com/dhui/dktest v0.4.6/go.mod h1:JHTSYDtKkvFNFHJKqCzVzqXecyv+tKt8EzceOmQOgbU=
github.com/distribution/reference v0.6.0 h1:0IXCQ5g4/QMHHkarYzh5l+u8T3t73zM5QvfrDyIgxBk=
github.com/distribution/reference v0.6.0/go.mod h1:BbU0aIcezP1/5jX/8MP0YiH4SdvB5Y4f/wlDRiLyi3E=
github.com/docker/docker v28.3.3+incompatible h1:Dypm25kh4rmk49v1eiVbsAtpAsYURjYkaKubwuBdxEI=
github.com/docker/docker v28.3.3+incompatible/go.mod h1:eEKB0N0r5NX/I1kEveEz05bcu8tLC/8azJZsviup8Sk=
github.com/docker/go-connections v0.5.0 h1:USnMq7hx7gwdVZq1L49hLXaFtUdTADjXGp+uj1Br63c=
github.com/docker/go-connections v0.5.0/go.mod h1:ov60Kzw0kKElRwhNs9UlUHAE/F9Fe6GLaXnqyDdmEXc=
github.com/docker/go-units v0.5.0 h1:69rxXcBk27SvSaaxTtLh/8llcHD8vYHT7WSdRZ/jvr4=
github.com/docker/go-units v0.5.0/go.mod h1:fgPhTUdO+D/Jk86RDLlptpiXQzgHJF7gydDDbaIK4Dk=
github.com/felixge/httpsnoop v1.0.4 h1:NFTV2Zj1bL4mc9sqWACXbQFVBBg2W3GPvqp8/ESS2Wg=
github.com/felixge/httpsnoop v1.0.4/go.mod h1:m8KPJKqk1gH5J9DgRY2ASl2lWCfGKXixSwevea8zH2U=
github.com/go-logr/logr v1.4.3 h1:CjnDlHq8ikf6E492q6eKboGOC0T8CDaOvkHCIg8idEI=
github.com/go-logr/logr v1.4.3/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
github.com/go-logr/stdr v1.2.2 h1:hSWxHoqTgW2S2qGc0LTAI563KZ5YKYRhT3MFKZMbjag=
github.com/go-logr/stdr v1.2.2/go.mod h1:mMo/vtBO5dYbehREoey6XUKy/eSumjCCveDpRre4VKE=
github.com/gogo/protobuf v1.3.2 h1:Ov1cvc58UF3b5XjBnZv7+opcTcQFZebYjWzi34vdm4Q=
github.com/gogo/protobuf v1.3.2/go.mod h1:P1XiOD3dCwIKUDQYPy72D8LYyHL2YPYrpS2s69NZV8Q=
github.com/golang-migrate/migrate/v4 v4.19.1 h1:OCyb44lFuQfYXYLx1SCxPZQGU7mcaZ7gH9yH4jSFbBA=
github.com/golang-migrate/migrate/v4 v4.19.1/go.mod h1:CTcgfjxhaUtsLipnLoQRWCrjYXycRz/g5+RWDuYgPrE=
github.com/golang/protobuf v1.5.4 h1:i7eJL8qZTpSEXOPTxNKhASYpMn+8e5Q6AdndVa1dWek=
github.com/golang/protobuf v1.5.4/go.mod h1:lnTiLA8Wa4RWRcIUkrtSVa5nRhsEGBg48fD6rSs7xps=
github.com/google/go-cmp v0.7.0 h1:wk8382ETsv4JYUZwIsn6YpYiWiBsYLSJiTsyBybVuN8=
github.com/google/go-cmp v0.7.0/go.mod h1:pXiqmnSA92OHEEa9HXL2W4E7lf9JzCmGVUdgjX3N/iU=
github.com/google/uuid v1.6.0 h1:NIvaJDMOsjHA8n1jAhLSgzrAzy1Hgr+hNrb57e+94F0=
github.com/google/uuid v1.6.0/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
github.com/ilyakaznacheev/cleanenv v1.5.0 h1:0VNZXggJE2OYdXE87bfSSwGxeiGt9moSR2lOrsHHvr4=
github.com/ilyakaznacheev/cleanenv v1.5.0/go.mod h1:a5aDzaJrLCQZsazHol1w8InnDcOX0OColm64SlIi6gk=
github.com/joho/godotenv v1.5.1 h1:7eLL/+HRGLY0ldzfGMeQkb7vMd0as4CfYvUVzLqw0N0=
github.com/joho/godotenv v1.5.1/go.mod h1:f4LDr5Voq0i2e/R5DDNOoa2zzDfwtkZa6DnEwAbqwq4=
github.com/lib/pq v1.10.9 h1:YXG7RB+JIjhP29X+OtkiDnYaXQwpS4JEWq7dtCCRUEw=
github.com/lib/pq v1.10.9/go.mod h1:AlVN5x4E4T544tWzH6hKfbfQvm3HdbOxrmggDNAPY9o=
github.com/moby/docker-image-spec v1.3.1 h1:jMKff3w6PgbfSa69GfNg+zN/XLhfXJGnEx3Nl2EsFP0=
github.com/moby/docker-image-spec v1.3.1/go.mod h1:eKmb5VW8vQEh/BAr2yvVNvuiJuY6UIocYsFu/DxxRpo=
github.com/moby/term v0.5.0 h1:xt8Q1nalod/v7BqbG21f8mQPqH+xAaC9C3N3wfWbVP0=
github.com/moby/term v0.5.0/go.mod h1:8FzsFHVUBGZdbDsJw/ot+X+d5HLUbvklYLJ9uGfcI3Y=
github.com/morikuni/aec v1.0.0 h1:nP9CBfwrvYnBRgY6qfDQkygYDmYwOilePFkwzv4dU8A=
github.com/morikuni/aec v1.0.0/go.mod h1:BbKIizmSmc5MMPqRYbxO4ZU0S0+P200+tUnFx7PXmsc=
github.com/opencontainers/go-digest v1.0.0 h1:apOUWs51W5PlhuyGyz9FCeeBIOUDA/6nW8Oi/yOhh5U=
github.com/opencontainers/go-digest v1.0.0/go.mod h1:0JzlMkj0TRzQZfJkVvzbP0HBR3IKzErnv2BNG4W4MAM=
github.com/opencontainers/image-spec v1.1.0 h1:8SG7/vwALn54lVB/0yZ/MMwhFrPYtpEHQb2IpWsCzug=
github.com/opencontainers/image-spec v1.1.0/go.mod h1:W4s4sFTMaBeK1BQLXbG4AdM2szdn85PY75RI83NrTrM=
github.com/pkg/errors v0.9.1 h1:FEBLx1zS214owpjy7qsBeixbURkuhQAwrK5UwLGTwt4=
github.com/pkg/errors v0.9.1/go.mod h1:bwawxfHBFNV+L2hUp1rHADufV3IMtnDRdf1r5NINEl0=
github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2 h1:Jamvg5psRIccs7FGNTlIRMkT8wgtp5eCXdBlqhYGL6U=
github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
github.com/stretchr/testify v1.10.0 h1:Xv5erBjTwe/5IxqUQTdXv5kgmIvbHo3QQyRwhJsOfJA=
github.com/stretchr/testify v1.10.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
go.opentelemetry.io/auto/sdk v1.2.1 h1:jXsnJ4Lmnqd11kwkBV2LgLoFMZKizbCi5fNZ/ipaZ64=
go.opentelemetry.io/auto/sdk v1.2.1/go.mod h1:KRTj+aOaElaLi+wW1kO/DZRXwkF4C5xPbEe3ZiIhN7Y=
go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.61.0 h1:F7Jx+6hwnZ41NSFTO5q4LYDtJRXBf2PD0rNBkeB/lus=
go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.61.0/go.mod h1:UHB22Z8QsdRDrnAtX4PntOl36ajSxcdUMt1sF7Y6E7Q=
go.opentelemetry.io/otel v1.39.0 h1:8yPrr/S0ND9QEfTfdP9V+SiwT4E0G7Y5MO7p85nis48=
go.opentelemetry.io/otel v1.39.0/go.mod h1:kLlFTywNWrFyEdH0oj2xK0bFYZtHRYUdv1NklR/tgc8=
go.opentelemetry.io/otel/metric v1.39.0 h1:d1UzonvEZriVfpNKEVmHXbdf909uGTOQjA0HF0Ls5Q0=
go.opentelemetry.io/otel/metric v1.39.0/go.mod h1:jrZSWL33sD7bBxg1xjrqyDjnuzTUB0x1nBERXd7Ftcs=
go.opentelemetry.io/otel/sdk v1.39.0 h1:nMLYcjVsvdui1B/4FRkwjzoRVsMK8uL/cj0OyhKzt18=
go.opentelemetry.io/otel/sdk v1.39.0/go.mod h1:vDojkC4/jsTJsE+kh+LXYQlbL8CgrEcwmt1ENZszdJE=
go.opentelemetry.io/otel/sdk/metric v1.39.0 h1:cXMVVFVgsIf2YL6QkRF4Urbr/aMInf+2WKg+sEJTtB8=
go.opentelemetry.io/otel/sdk/metric v1.39.0/go.mod h1:xq9HEVH7qeX69/JnwEfp6fVq5wosJsY1mt4lLfYdVew=
go.opentelemetry.io/otel/trace v1.39.0 h1:2d2vfpEDmCJ5zVYz7ijaJdOF59xLomrvj7bjt6/qCJI=
go.opentelemetry.io/otel/trace v1.39.0/go.mod h1:88w4/PnZSazkGzz/w84VHpQafiU4EtqqlVdxWy+rNOA=
golang.org/x/net v0.48.0 h1:zyQRTTrjc33Lhh0fBgT/H3oZq9WuvRR5gPC70xpDiQU=
golang.org/x/net v0.48.0/go.mod h1:+ndRgGjkh8FGtu1w1FGbEC31if4VrNVMuKTgcAAnQRY=
golang.org/x/sys v0.39.0 h1:CvCKL8MeisomCi6qNZ+wbb0DN9E5AATixKsvNtMoMFk=
golang.org/x/sys v0.39.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
golang.org/x/text v0.32.0 h1:ZD01bjUt1FQ9WJ0ClOL5vxgxOI/sVCNgX1YtKwcY0mU=
golang.org/x/text v0.32.0/go.mod h1:o/rUWzghvpD5TXrTIBuJU77MTaN0ljMWE47kxGJQ7jY=
gonum.org/v1/gonum v0.16.0 h1:5+ul4Swaf3ESvrOnidPp4GZbzf0mxVQpDCYUQE7OJfk=
gonum.org/v1/gonum v0.16.0/go.mod h1:fef3am4MQ93R2HHpKnLk4/Tbh/s0+wqD5nfa6Pnwy4E=
google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217 h1:gRkg/vSppuSQoDjxyiGfN4Upv/h/DQmIR10ZU8dh4Ww=
google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217/go.mod h1:7i2o+ce6H/6BluujYR+kqX3GKH+dChPTQU19wjRPiGk=
google.golang.org/grpc v1.79.1 h1:zGhSi45ODB9/p3VAawt9a+O/MULLl9dpizzNNpq7flY=
google.golang.org/grpc v1.79.1/go.mod h1:KmT0Kjez+0dde/v2j9vzwoAScgEPx/Bw1CYChhHLrHQ=
google.golang.org/protobuf v1.36.11 h1:fV6ZwhNocDyBLK0dj+fg8ektcVegBBuEolpbTQyBNVE=
google.golang.org/protobuf v1.36.11/go.mod h1:HTf+CrKn2C3g5S8VImy6tdcUvCska2kB7j23XfzDpco=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405 h1:yhCVgyC4o1eVCa2tZl7eS0r+SDo693bJlVdllGtEeKM=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
olympos.io/encoding/edn v0.0.0-20201019073823-d3554ca0b0a3 h1:slmdOY3vp8a7KQbHkL+FLbvbkgMqmXojpFUO/jENuqQ=
olympos.io/encoding/edn v0.0.0-20201019073823-d3554ca0b0a3/go.mod h1:oVgVk4OWVDi43qWBEyGhXgYxt7+ED4iYNpTngSLX2Iw=

### .\Backend\database\go.sum END ###

### .\Backend\database\internal\app\app.go BEGIN ###
package app

// Error code 2000
import (
	grpcapp "database/internal/app/grpc"
	"database/internal/config"
	dbrepo "database/internal/repository"
	servicesdb "database/internal/services"
)

type App struct {
	GRPCServer *grpcapp.App
}

func New(cfg config.DatabaseConfig, port int) *App {
	dbr := dbrepo.New(cfg)
	dbservice := servicesdb.New(dbr)
	grpcapp := grpcapp.New(dbservice, port)
	return &App{GRPCServer: grpcapp}
}

### .\Backend\database\internal\app\app.go END ###

### .\Backend\database\internal\app\grpc\app.go BEGIN ###
package grpcapp

// Error code 2500
import (
	"context"
	grpchandler "database/internal/handlers/grpc"
	"fmt"
	"net"
	"time"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

type App struct {
	grpcServer *grpc.Server
	port       int
}

func New(serverAPI grpchandler.DatabaseService, port int) *App {
	opts := []grpc.ServerOption{grpc.UnaryInterceptor(loggingInterceptor())}
	gRPCServer := grpc.NewServer(opts...)
	grpchandler.Register(gRPCServer, serverAPI)
	return &App{grpcServer: gRPCServer, port: port}
}

func (a *App) MustRun() {
	if err := a.Run(); err != nil {
		logger.Fatal("Failed to run gRPC server", err, 2500, nil)
	}
}

func (a *App) Run() error {
	logger.Info("Starting gRPC server", map[string]any{"port": a.port})
	l, err := net.Listen("tcp", fmt.Sprintf(":%d", a.port))
	if err != nil {
		logger.Error("Error starting listener for gRPC server", err, 2502, map[string]any{"port": a.port})
		return err
	}
	logger.Debug("gRPC server is starting", 2503, map[string]any{"address": l.Addr().String()})
	if err := a.grpcServer.Serve(l); err != nil {
		logger.Error("Error starting gRPC server", err, 2504, nil)
		return err
	}
	logger.Info("gRPC server is runned", map[string]any{"address": l.Addr().String()})
	return nil
}

func (a *App) Stop() error {
	logger.Info("Stopping the gRPC server", nil)
	logger.Debug("gRPC server is stopping", 2505, nil)
	a.grpcServer.GracefulStop()
	logger.Debug("gRPC server is stopped", 2506, nil)
	return nil
}

func loggingInterceptor() grpc.UnaryServerInterceptor {
	return func(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
		start := time.Now()
		resp, err := handler(ctx, req)
		duration := time.Since(start)
		if req == nil {
			logger.Warn("gRPC request without data", 2506, map[string]any{"method": info.FullMethod})
		}
		fields := map[string]any{
			"method":   info.FullMethod,
			"duration": duration.String(),
			"req":      req,
		}
		if err != nil {
			st, ok := status.FromError(err)
			if ok {
				fields["grpc_code"] = st.Code().String()
			} else {
				fields["grpc_code"] = codes.Unknown.String()
			}
			logger.Error("gRPC request failed", err, 2506, fields)
		} else {
			fields["grpc_code"] = codes.OK.String()
			logger.Info("gRPC request success", fields)
		}
		return resp, err
	}
}

### .\Backend\database\internal\app\grpc\app.go END ###

### .\Backend\database\internal\config\config.go BEGIN ###
package config

import (
	"flag"
	"os"
	"time"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	Env        string         `yaml:"env" env-default:"local"`           // debug, local, test, production
	FormatTime string         `yaml:"format_time" env-default:"RFC3339"` // time format
	FilePath   string         `yaml:"file_path" env-default:"app.log"`   // log file path
	GRPC       GRPCConfig     `yaml:"grpc"`                              // gRPC config
	Database   DatabaseConfig `yaml:"postgres" env-required:"true"`      // database config
}

type GRPCConfig struct {
	Port    int `yaml:"port"`    // gRPC port
	Timeout int `yaml:"timeout"` // gRPC timeout
}

type DatabaseConfig struct {
	Host           string `yaml:"host" env-required:"true"`            // database host
	Port           int    `yaml:"port" env-required:"true"`            // database port
	User           string `yaml:"user" env-required:"true"`            // database user
	Password       string `yaml:"password" env-required:"true"`        // database password
	Database       string `yaml:"database" env-required:"true"`        // database name
	MigrationsPath string `yaml:"migrations_path" env-required:"true"` // migrations path
}

var level logger.Level

var timeLayouts = map[string]string{
	"Layout":      time.Layout,
	"ANSIC":       time.ANSIC,
	"UnixDate":    time.UnixDate,
	"RubyDate":    time.RubyDate,
	"RFC822":      time.RFC822,
	"RFC822Z":     time.RFC822Z,
	"RFC850":      time.RFC850,
	"RFC1123":     time.RFC1123,
	"RFC1123Z":    time.RFC1123Z,
	"RFC3339":     time.RFC3339,
	"RFC3339Nano": time.RFC3339Nano,
	"Kitchen":     time.Kitchen,
	"Stamp":       time.Stamp,
	"StampMilli":  time.StampMilli,
	"StampMicro":  time.StampMicro,
	"StampNano":   time.StampNano,
	"DataTime":    time.DateTime,
	"DataOnly":    time.DateOnly,
	"TimeOnly":    time.TimeOnly,
}

func getTimeLayout(configValue string) string {
	if layout, ok := timeLayouts[configValue]; ok {
		return layout
	}
	return time.RFC3339
}

func relevel(l string) logger.Level {
	if l == "" {
		l = "local"
	}
	switch l {
	case "debug":
		level = logger.LevelDebug
	case "local":
		level = logger.LevelInfo
	case "test":
		level = logger.LevelWarn
	case "production":
		level = logger.LevelError
	}
	return level
}

func MustLoad() (*Config, logger.Level) {
	path := fechPathConfig()
	if path == "" {
		panic("config path is empty")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		panic("config file not found: " + path)
	}
	var cfg Config
	if err := cleanenv.ReadConfig(path, &cfg); err != nil {
		panic("failed to load config: " + err.Error())
	}
	cfg.FormatTime = getTimeLayout(cfg.FormatTime)
	return &cfg, relevel(cfg.Env)
}

func fechPathConfig() string {
	var res string
	//--config="path/to/config.yaml"
	flag.StringVar(&res, "config", "", "path to config file")
	flag.Parse()
	return res
}

### .\Backend\database\internal\config\config.go END ###

### .\Backend\database\internal\handlers\grpc\server.go BEGIN ###
package grpchandler

import (
	"context"
	database1 "database/contract"
	"database/internal/models"
	"encoding/json"
	"fmt"

	"google.golang.org/grpc"
)

type DatabaseService interface {
	CreateUser(ctx context.Context, user models.User) error
	GetUserByLogin(ctx context.Context, login string) (models.User, error)
	CreateQuery(ctx context.Context, userID string) (int64, error)
	GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error)
}

type serverAPI struct {
	database1.UnimplementedDatabaseServer
	database DatabaseService
}

func Register(srv *grpc.Server, database DatabaseService) {
	database1.RegisterDatabaseServer(srv, &serverAPI{database: database})
}

func (s *serverAPI) CreateUser(ctx context.Context, req *database1.CreateUserRequest) (*database1.CreateUserResponse, error) {
	var user models.User
	if err := json.Unmarshal(req.Data, &user); err != nil {
		return nil, fmt.Errorf("failed to decode user data: %w", err)
	}

	if err := s.database.CreateUser(ctx, user); err != nil {
		return nil, fmt.Errorf("failed to create user: %w", err)
	}

	return &database1.CreateUserResponse{Message: "Success"}, nil
}

func (s *serverAPI) CheckUser(ctx context.Context, req *database1.CheckUserRequest) (*database1.CheckUserResponse, error) {
	var requestData map[string]string
	if err := json.Unmarshal(req.Data, &requestData); err != nil {
		return nil, fmt.Errorf("failed to decode login data: %w", err)
	}

	user, err := s.database.GetUserByLogin(ctx, requestData["login"])
	if err != nil {
		return nil, fmt.Errorf("user not found or db error: %w", err)
	}

	responseData, _ := json.Marshal(user)
	return &database1.CheckUserResponse{
		Message: "Success",
		Data:    responseData,
	}, nil
}

func (s *serverAPI) AddNewData(ctx context.Context, req *database1.AddNewAnswerRequest) (*database1.AddNewAnswerResponse, error) {
	var requestData map[string]string
	if err := json.Unmarshal(req.Data, &requestData); err != nil {
		return nil, fmt.Errorf("failed to decode user id: %w", err)
	}

	queryID, err := s.database.CreateQuery(ctx, requestData["user_id"])
	if err != nil {
		return nil, fmt.Errorf("failed to register query: %w", err)
	}

	return &database1.AddNewAnswerResponse{
		Message: fmt.Sprintf("%d", queryID),
	}, nil
}

func (s *serverAPI) RequestOldDatas(ctx context.Context, req *database1.RequestOldAnswersRequest) (*database1.RequestOldAnswersResponse, error) {
	var (
		quantity int64  = req.GetQuantity()
		userID   string = req.GetUserID()
		flag     string = req.GetFlag()
	)
	if quantity == 0 || userID == "" || flag == "" {
		return nil, fmt.Errorf("invalid request parameters")
	}

	answers, err := s.database.GetHistoryAnswers(ctx, quantity, userID, flag)
	if err != nil {
		return nil, fmt.Errorf("failed to get history answers: %w", err)
	}

	responseData, err := json.Marshal(answers)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal answers: %w", err)
	}
	return &database1.RequestOldAnswersResponse{
		Message: "Success",
		Data:    responseData,
	}, nil
}

### .\Backend\database\internal\handlers\grpc\server.go END ###

### .\Backend\database\internal\migrations\1_init_schema.down.sql BEGIN ###
DROP TABLE IF EXISTS queries;
DROP TABLE IF EXISTS users;
DROP EXTENSION IF EXISTS "uuid-ossp";
### .\Backend\database\internal\migrations\1_init_schema.down.sql END ###

### .\Backend\database\internal\migrations\1_init_schema.up.sql BEGIN ###
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    login VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS queries (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
### .\Backend\database\internal\migrations\1_init_schema.up.sql END ###

### .\Backend\database\internal\migrator\migrator.go BEGIN ###
package migrator

// Error code 4000
import (
	"database/sql"
	"errors"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/golang-migrate/migrate/v4"
	"github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	_ "github.com/lib/pq"
)

var migrationsPathDefault string = "./migrations"

func Run(db *sql.DB, migrationsPath string) error {
	logger.Info("Running migrations for the database", nil)
	logger.Debug("Checking if db is nil", 4000, nil)
	if db == nil {
		err := errors.New("db is nil")
		logger.Error("Could not run migrations", err, 4001, nil)
		return err
	}
	logger.Debug("Checking if migrations path is empty", 4002, nil)
	if migrationsPath == "" {
		logger.Warn("Migrations path is empty, using default path", 4003, nil)
		migrationsPath = migrationsPathDefault
	}
	logger.Debug("Creating database driver", 4004, nil)
	driver, err := postgres.WithInstance(db, &postgres.Config{})
	if err != nil {
		logger.Error("Could not create database driver", err, 4005, nil)
		return err
	}
	logger.Debug("Creating migrate instance", 4006, map[string]any{"migrations_path": migrationsPath})
	m, err := migrate.NewWithDatabaseInstance(
		migrationsPath,
		"postgres",
		driver,
	)
	if err != nil {
		logger.Error("Could not create migrate instance", err, 4007, map[string]any{"migrations_path": migrationsPath})
		return err
	}
	logger.Debug("Running migrations", 4008, nil)
	err = m.Up()
	if err == nil || errors.Is(err, migrate.ErrNoChange) {
		logger.Info("Migrations completed", nil)
		return nil
	}
	logger.Error("Migrations failed", err, 4009, nil)
	logger.Warn("Trying to force rollback to previous version", 4009, nil)
	logger.Debug("Getting migrate version", 4009, nil)
	version, dirty, verErr := m.Version()
	if verErr != nil {
		logger.Error("Could not get migrate version", verErr, 4010, nil)
		return verErr
	}
	logger.Debug("Migrate version", 4011, map[string]any{"version": version, "dirty": dirty})
	if dirty {
		logger.Warn("Dirty migration detected", 4012, map[string]any{"version": version})
		prevVersion := int(version) - 1
		logger.Debug("Forcing rollback to previous version", 4013, map[string]any{"version": prevVersion})
		if prevVersion < 0 {
			logger.Warn("Previous version is less than 0, setting it to 0", 4014, nil)
			prevVersion = 0
		}
		logger.Debug("Forcing rollback to previous version", 4015, map[string]any{"version": prevVersion})
		if forceErr := m.Force(prevVersion); forceErr != nil {
			logger.Error("Could not force rollback to previous version", forceErr, 4016, map[string]any{"version": prevVersion})
			return forceErr
		}
		logger.Warn("Forced rollback to previous version successfully", 4017, map[string]any{"version": prevVersion})
		return err
	}
	logger.Error("Could not force rollback to previous version", err, 4018, map[string]any{"version": version})
	return err
}

### .\Backend\database\internal\migrator\migrator.go END ###

### .\Backend\database\internal\models\models.go BEGIN ###
package models

type User struct {
	ID           string `json:"id"`
	Login        string `json:"login"`
	PasswordHash string `json:"password_hash"`
}

type Query struct {
	ID     int64  `json:"id"`
	UserID string `json:"user_id"`
}

### .\Backend\database\internal\models\models.go END ###

### .\Backend\database\internal\repository\database.go BEGIN ###
package dbrepo

import (
	"context"
	"database/internal/config"
	"database/internal/migrator"
	"database/internal/models"
	"database/sql"
	"fmt"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
)

type DatabaseRepo struct {
	db *sql.DB
}

func New(cfg config.DatabaseConfig) *DatabaseRepo {
	logger.Info("Initializing database", nil)
	logger.Debug("Connecting to the database", 6000, map[string]any{
		"host":            cfg.Host,
		"port":            cfg.Port,
		"user":            cfg.User,
		"database":        cfg.Database,
		"migrations_path": cfg.MigrationsPath,
	})
	connstr := fmt.Sprintf(
		"host=%s port=%d dbname=%s user=%s password=%s sslmode=disable",
		cfg.Host,
		cfg.Port,
		cfg.Database,
		cfg.User,
		cfg.Password,
	)
	db, err := sql.Open("postgres", connstr)
	if err != nil {
		logger.Fatal("Failed to connect to the database", err, 6001, map[string]any{"connstr": connstr})
	}
	if err := db.Ping(); err != nil {
		logger.Fatal("Failed to ping database", err, 6002, map[string]any{"connstr": connstr})
	}
	logger.Info("Connected to the database successfully", nil)
	logger.Debug("Running migrations", 6003, map[string]any{"migrations_path": cfg.MigrationsPath})
	err = migrator.Run(db, cfg.MigrationsPath)
	if err != nil {
		logger.Fatal("Failed to migrate the database", err, 6004, map[string]any{"migrations_path": cfg.MigrationsPath})
	}
	logger.Info("Database migration completed", nil)
	return &DatabaseRepo{db: db}
}

func (r *DatabaseRepo) CreateUser(ctx context.Context, user models.User) error {
	query := `INSERT INTO users (login, password_hash) VALUES ($1, $2)`
	_, err := r.db.ExecContext(ctx, query, user.Login, user.PasswordHash)
	return err
}

func (r *DatabaseRepo) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	query := `SELECT id, login, password_hash FROM users WHERE login = $1`
	var user models.User
	err := r.db.QueryRowContext(ctx, query, login).Scan(&user.ID, &user.Login, &user.PasswordHash)
	return user, err
}

func (r *DatabaseRepo) CreateQuery(ctx context.Context, userID string) (int64, error) {
	query := `INSERT INTO queries (user_id) VALUES ($1) RETURNING id`
	var queryID int64
	err := r.db.QueryRowContext(ctx, query, userID).Scan(&queryID)
	return queryID, err
}

func (r *DatabaseRepo) GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error) {
	query := `SELECT id FROM queries WHERE user_id = $1 ORDER BY id DESC LIMIT $2`
	var ids []int32
	rows, err := r.db.QueryContext(ctx, query, userID, quantity)
	if err != nil {
		return nil, err
	}
	for rows.Next() {
		var id int32
		err := rows.Scan(&id)
		if err != nil {
			return nil, err
		}
		ids = append(ids, id)
	}
	return ids, nil
}

### .\Backend\database\internal\repository\database.go END ###

### .\Backend\database\internal\services\database.go BEGIN ###
package servicesdb

import (
	"context"
	"database/internal/models"
	dbrepo "database/internal/repository"
)

type Database struct {
	usercreate  UserCreator
	userget     UserGetter
	querycreate QueryCreator
	historyget  HistoryGetter
}

func New(db *dbrepo.DatabaseRepo) *Database {
	return &Database{
		usercreate:  db,
		userget:     db,
		querycreate: db,
		historyget:  db,
	}
}

type UserCreator interface {
	CreateUser(ctx context.Context, user models.User) error
}

type UserGetter interface {
	GetUserByLogin(ctx context.Context, login string) (models.User, error)
}

type QueryCreator interface {
	CreateQuery(ctx context.Context, userID string) (int64, error)
}

type HistoryGetter interface {
	GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error)
}

func (s *Database) CreateUser(ctx context.Context, user models.User) error {
	return s.usercreate.CreateUser(ctx, user)
}

func (s *Database) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	return s.userget.GetUserByLogin(ctx, login)
}

func (s *Database) CreateQuery(ctx context.Context, userID string) (int64, error) {
	return s.querycreate.CreateQuery(ctx, userID)
}

func (s *Database) GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error) {
	return s.historyget.GetHistoryAnswers(ctx, quantity, userID, flag)
}

### .\Backend\database\internal\services\database.go END ###

### .\Backend\manager\cmd\main.go BEGIN ###
package main

import (
	"fmt"
	"manager/internal/app"
	"manager/internal/config"
	"os"
	"os/signal"
	"syscall"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
)

func main() {
	cfg, level := config.MustLoad()
	err := logger.Init(level, cfg.Env, cfg.LogFilePath)
	if err != nil {
		fmt.Printf("Failed to init logger: %v\n", err)
		return
	}
	defer func() {
		if err := logger.Close(); err != nil {
			fmt.Printf("Failed to close logger: %v\n", err)
		}
	}()
	logger.Info("Config has been successfully loaded", nil)
	logger.Debug("Config data", 1000, map[string]any{
		"env":                  cfg.Env,
		"format_time":          cfg.FormatTime,
		"file_path":            cfg.LogFilePath,
		"httpserver_port":      cfg.HttpServer.Port,
		"httpserver_host":      cfg.HttpServer.Host,
		"client_database_host": cfg.Client.Database.Host,
		"client_database_port": cfg.Client.Database.Port,
		"client_ml_host":       cfg.Client.ML.Host,
		"client_ml_port":       cfg.Client.ML.Port,
	})
	application := app.New(cfg)
	defer application.Close()
	logger.Info("Application has been successfully initialized", nil)
	go func() {
		application.HTTPApp.MustRun()
	}()
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGTERM, syscall.SIGINT)
	<-stop
	logger.Info("Gracefully stopped", nil)
}

### .\Backend\manager\cmd\main.go END ###

### .\Backend\manager\config\config.yaml BEGIN ###
env: "local" # debug, local, test, production
format_time: "RFC3339"
log_file_path: "app.log"
temp_object_path: "volume"
jwt_secret: "xui"

httpserver:
  port: 8080
  host: localhost

client:
  database:
    host: db_service
    port: 2021

  ml:
    host: ml
    port: 50051
### .\Backend\manager\config\config.yaml END ###

### .\Backend\manager\contract\database\database.pb.go BEGIN ###
// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.36.10
// 	protoc        v6.33.1
// source: newp/database/database.proto

package database1

import (
	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
	reflect "reflect"
	sync "sync"
	unsafe "unsafe"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type CreateUserRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CreateUserRequest) Reset() {
	*x = CreateUserRequest{}
	mi := &file_newp_database_database_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CreateUserRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CreateUserRequest) ProtoMessage() {}

func (x *CreateUserRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CreateUserRequest.ProtoReflect.Descriptor instead.
func (*CreateUserRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{0}
}

func (x *CreateUserRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *CreateUserRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type CreateUserResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CreateUserResponse) Reset() {
	*x = CreateUserResponse{}
	mi := &file_newp_database_database_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CreateUserResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CreateUserResponse) ProtoMessage() {}

func (x *CreateUserResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CreateUserResponse.ProtoReflect.Descriptor instead.
func (*CreateUserResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{1}
}

func (x *CreateUserResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

type CheckUserRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CheckUserRequest) Reset() {
	*x = CheckUserRequest{}
	mi := &file_newp_database_database_proto_msgTypes[2]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CheckUserRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CheckUserRequest) ProtoMessage() {}

func (x *CheckUserRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[2]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CheckUserRequest.ProtoReflect.Descriptor instead.
func (*CheckUserRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{2}
}

func (x *CheckUserRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *CheckUserRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type CheckUserResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *CheckUserResponse) Reset() {
	*x = CheckUserResponse{}
	mi := &file_newp_database_database_proto_msgTypes[3]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *CheckUserResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*CheckUserResponse) ProtoMessage() {}

func (x *CheckUserResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[3]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use CheckUserResponse.ProtoReflect.Descriptor instead.
func (*CheckUserResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{3}
}

func (x *CheckUserResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

func (x *CheckUserResponse) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type DeleteUserRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *DeleteUserRequest) Reset() {
	*x = DeleteUserRequest{}
	mi := &file_newp_database_database_proto_msgTypes[4]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *DeleteUserRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*DeleteUserRequest) ProtoMessage() {}

func (x *DeleteUserRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[4]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use DeleteUserRequest.ProtoReflect.Descriptor instead.
func (*DeleteUserRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{4}
}

func (x *DeleteUserRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *DeleteUserRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type DeleteUserResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *DeleteUserResponse) Reset() {
	*x = DeleteUserResponse{}
	mi := &file_newp_database_database_proto_msgTypes[5]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *DeleteUserResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*DeleteUserResponse) ProtoMessage() {}

func (x *DeleteUserResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[5]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use DeleteUserResponse.ProtoReflect.Descriptor instead.
func (*DeleteUserResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{5}
}

func (x *DeleteUserResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

type AddNewAnswerRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *AddNewAnswerRequest) Reset() {
	*x = AddNewAnswerRequest{}
	mi := &file_newp_database_database_proto_msgTypes[6]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *AddNewAnswerRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*AddNewAnswerRequest) ProtoMessage() {}

func (x *AddNewAnswerRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[6]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use AddNewAnswerRequest.ProtoReflect.Descriptor instead.
func (*AddNewAnswerRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{6}
}

func (x *AddNewAnswerRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *AddNewAnswerRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type AddNewAnswerResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *AddNewAnswerResponse) Reset() {
	*x = AddNewAnswerResponse{}
	mi := &file_newp_database_database_proto_msgTypes[7]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *AddNewAnswerResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*AddNewAnswerResponse) ProtoMessage() {}

func (x *AddNewAnswerResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[7]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use AddNewAnswerResponse.ProtoReflect.Descriptor instead.
func (*AddNewAnswerResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{7}
}

func (x *AddNewAnswerResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

type RequestOldAnswersRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Quantity      int64                  `protobuf:"varint,1,opt,name=Quantity,proto3" json:"Quantity,omitempty"`
	Flag          string                 `protobuf:"bytes,2,opt,name=Flag,proto3" json:"Flag,omitempty"`
	UserID        string                 `protobuf:"bytes,3,opt,name=UserID,proto3" json:"UserID,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestOldAnswersRequest) Reset() {
	*x = RequestOldAnswersRequest{}
	mi := &file_newp_database_database_proto_msgTypes[8]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestOldAnswersRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestOldAnswersRequest) ProtoMessage() {}

func (x *RequestOldAnswersRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[8]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestOldAnswersRequest.ProtoReflect.Descriptor instead.
func (*RequestOldAnswersRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{8}
}

func (x *RequestOldAnswersRequest) GetQuantity() int64 {
	if x != nil {
		return x.Quantity
	}
	return 0
}

func (x *RequestOldAnswersRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *RequestOldAnswersRequest) GetUserID() string {
	if x != nil {
		return x.UserID
	}
	return ""
}

type RequestOldAnswersResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	Data          []byte                 `protobuf:"bytes,2,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestOldAnswersResponse) Reset() {
	*x = RequestOldAnswersResponse{}
	mi := &file_newp_database_database_proto_msgTypes[9]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestOldAnswersResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestOldAnswersResponse) ProtoMessage() {}

func (x *RequestOldAnswersResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[9]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestOldAnswersResponse.ProtoReflect.Descriptor instead.
func (*RequestOldAnswersResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{9}
}

func (x *RequestOldAnswersResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

func (x *RequestOldAnswersResponse) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type RequestDeletedAnswersRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Flag          string                 `protobuf:"bytes,1,opt,name=Flag,proto3" json:"Flag,omitempty"`
	UserID        string                 `protobuf:"bytes,2,opt,name=UserID,proto3" json:"UserID,omitempty"`
	Data          []byte                 `protobuf:"bytes,3,opt,name=Data,proto3" json:"Data,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestDeletedAnswersRequest) Reset() {
	*x = RequestDeletedAnswersRequest{}
	mi := &file_newp_database_database_proto_msgTypes[10]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestDeletedAnswersRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestDeletedAnswersRequest) ProtoMessage() {}

func (x *RequestDeletedAnswersRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[10]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestDeletedAnswersRequest.ProtoReflect.Descriptor instead.
func (*RequestDeletedAnswersRequest) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{10}
}

func (x *RequestDeletedAnswersRequest) GetFlag() string {
	if x != nil {
		return x.Flag
	}
	return ""
}

func (x *RequestDeletedAnswersRequest) GetUserID() string {
	if x != nil {
		return x.UserID
	}
	return ""
}

func (x *RequestDeletedAnswersRequest) GetData() []byte {
	if x != nil {
		return x.Data
	}
	return nil
}

type RequestDeletedAnswersResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	Message       string                 `protobuf:"bytes,1,opt,name=Message,proto3" json:"Message,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *RequestDeletedAnswersResponse) Reset() {
	*x = RequestDeletedAnswersResponse{}
	mi := &file_newp_database_database_proto_msgTypes[11]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *RequestDeletedAnswersResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*RequestDeletedAnswersResponse) ProtoMessage() {}

func (x *RequestDeletedAnswersResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_database_database_proto_msgTypes[11]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use RequestDeletedAnswersResponse.ProtoReflect.Descriptor instead.
func (*RequestDeletedAnswersResponse) Descriptor() ([]byte, []int) {
	return file_newp_database_database_proto_rawDescGZIP(), []int{11}
}

func (x *RequestDeletedAnswersResponse) GetMessage() string {
	if x != nil {
		return x.Message
	}
	return ""
}

var File_newp_database_database_proto protoreflect.FileDescriptor

const file_newp_database_database_proto_rawDesc = "" +
	"\n" +
	"\x1cnewp/database/database.proto\x12\bdatabase\";\n" +
	"\x11CreateUserRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\".\n" +
	"\x12CreateUserResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\":\n" +
	"\x10CheckUserRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\"A\n" +
	"\x11CheckUserResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\";\n" +
	"\x11DeleteUserRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\".\n" +
	"\x12DeleteUserResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\"=\n" +
	"\x13AddNewAnswerRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\"0\n" +
	"\x14AddNewAnswerResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\"b\n" +
	"\x18RequestOldAnswersRequest\x12\x1a\n" +
	"\bQuantity\x18\x01 \x01(\x03R\bQuantity\x12\x12\n" +
	"\x04Flag\x18\x02 \x01(\tR\x04Flag\x12\x16\n" +
	"\x06UserID\x18\x03 \x01(\tR\x06UserID\"I\n" +
	"\x19RequestOldAnswersResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage\x12\x12\n" +
	"\x04Data\x18\x02 \x01(\fR\x04Data\"^\n" +
	"\x1cRequestDeletedAnswersRequest\x12\x12\n" +
	"\x04Flag\x18\x01 \x01(\tR\x04Flag\x12\x16\n" +
	"\x06UserID\x18\x02 \x01(\tR\x06UserID\x12\x12\n" +
	"\x04Data\x18\x03 \x01(\fR\x04Data\"9\n" +
	"\x1dRequestDeletedAnswersResponse\x12\x18\n" +
	"\aMessage\x18\x01 \x01(\tR\aMessage2\xf3\x03\n" +
	"\bDatabase\x12G\n" +
	"\n" +
	"CreateUser\x12\x1b.database.CreateUserRequest\x1a\x1c.database.CreateUserResponse\x12D\n" +
	"\tCheckUser\x12\x1a.database.CheckUserRequest\x1a\x1b.database.CheckUserResponse\x12G\n" +
	"\n" +
	"DeleteUser\x12\x1b.database.DeleteUserRequest\x1a\x1c.database.DeleteUserResponse\x12K\n" +
	"\n" +
	"AddNewData\x12\x1d.database.AddNewAnswerRequest\x1a\x1e.database.AddNewAnswerResponse\x12Z\n" +
	"\x0fRequestOldDatas\x12\".database.RequestOldAnswersRequest\x1a#.database.RequestOldAnswersResponse\x12f\n" +
	"\x13RequestDeletedDatas\x12&.database.RequestDeletedAnswersRequest\x1a'.database.RequestDeletedAnswersResponseB\x1eZ\x1csirius.database.v1;database1b\x06proto3"

var (
	file_newp_database_database_proto_rawDescOnce sync.Once
	file_newp_database_database_proto_rawDescData []byte
)

func file_newp_database_database_proto_rawDescGZIP() []byte {
	file_newp_database_database_proto_rawDescOnce.Do(func() {
		file_newp_database_database_proto_rawDescData = protoimpl.X.CompressGZIP(unsafe.Slice(unsafe.StringData(file_newp_database_database_proto_rawDesc), len(file_newp_database_database_proto_rawDesc)))
	})
	return file_newp_database_database_proto_rawDescData
}

var file_newp_database_database_proto_msgTypes = make([]protoimpl.MessageInfo, 12)
var file_newp_database_database_proto_goTypes = []any{
	(*CreateUserRequest)(nil),             // 0: database.CreateUserRequest
	(*CreateUserResponse)(nil),            // 1: database.CreateUserResponse
	(*CheckUserRequest)(nil),              // 2: database.CheckUserRequest
	(*CheckUserResponse)(nil),             // 3: database.CheckUserResponse
	(*DeleteUserRequest)(nil),             // 4: database.DeleteUserRequest
	(*DeleteUserResponse)(nil),            // 5: database.DeleteUserResponse
	(*AddNewAnswerRequest)(nil),           // 6: database.AddNewAnswerRequest
	(*AddNewAnswerResponse)(nil),          // 7: database.AddNewAnswerResponse
	(*RequestOldAnswersRequest)(nil),      // 8: database.RequestOldAnswersRequest
	(*RequestOldAnswersResponse)(nil),     // 9: database.RequestOldAnswersResponse
	(*RequestDeletedAnswersRequest)(nil),  // 10: database.RequestDeletedAnswersRequest
	(*RequestDeletedAnswersResponse)(nil), // 11: database.RequestDeletedAnswersResponse
}
var file_newp_database_database_proto_depIdxs = []int32{
	0,  // 0: database.Database.CreateUser:input_type -> database.CreateUserRequest
	2,  // 1: database.Database.CheckUser:input_type -> database.CheckUserRequest
	4,  // 2: database.Database.DeleteUser:input_type -> database.DeleteUserRequest
	6,  // 3: database.Database.AddNewData:input_type -> database.AddNewAnswerRequest
	8,  // 4: database.Database.RequestOldDatas:input_type -> database.RequestOldAnswersRequest
	10, // 5: database.Database.RequestDeletedDatas:input_type -> database.RequestDeletedAnswersRequest
	1,  // 6: database.Database.CreateUser:output_type -> database.CreateUserResponse
	3,  // 7: database.Database.CheckUser:output_type -> database.CheckUserResponse
	5,  // 8: database.Database.DeleteUser:output_type -> database.DeleteUserResponse
	7,  // 9: database.Database.AddNewData:output_type -> database.AddNewAnswerResponse
	9,  // 10: database.Database.RequestOldDatas:output_type -> database.RequestOldAnswersResponse
	11, // 11: database.Database.RequestDeletedDatas:output_type -> database.RequestDeletedAnswersResponse
	6,  // [6:12] is the sub-list for method output_type
	0,  // [0:6] is the sub-list for method input_type
	0,  // [0:0] is the sub-list for extension type_name
	0,  // [0:0] is the sub-list for extension extendee
	0,  // [0:0] is the sub-list for field type_name
}

func init() { file_newp_database_database_proto_init() }
func file_newp_database_database_proto_init() {
	if File_newp_database_database_proto != nil {
		return
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: unsafe.Slice(unsafe.StringData(file_newp_database_database_proto_rawDesc), len(file_newp_database_database_proto_rawDesc)),
			NumEnums:      0,
			NumMessages:   12,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_newp_database_database_proto_goTypes,
		DependencyIndexes: file_newp_database_database_proto_depIdxs,
		MessageInfos:      file_newp_database_database_proto_msgTypes,
	}.Build()
	File_newp_database_database_proto = out.File
	file_newp_database_database_proto_goTypes = nil
	file_newp_database_database_proto_depIdxs = nil
}

### .\Backend\manager\contract\database\database.pb.go END ###

### .\Backend\manager\contract\database\database_grpc.pb.go BEGIN ###
// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.5.1
// - protoc             v6.33.1
// source: newp/database/database.proto

package database1

import (
	context "context"
	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.64.0 or later.
const _ = grpc.SupportPackageIsVersion9

const (
	Database_CreateUser_FullMethodName          = "/database.Database/CreateUser"
	Database_CheckUser_FullMethodName           = "/database.Database/CheckUser"
	Database_DeleteUser_FullMethodName          = "/database.Database/DeleteUser"
	Database_AddNewData_FullMethodName          = "/database.Database/AddNewData"
	Database_RequestOldDatas_FullMethodName     = "/database.Database/RequestOldDatas"
	Database_RequestDeletedDatas_FullMethodName = "/database.Database/RequestDeletedDatas"
)

// DatabaseClient is the client API for Database service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type DatabaseClient interface {
	CreateUser(ctx context.Context, in *CreateUserRequest, opts ...grpc.CallOption) (*CreateUserResponse, error)
	CheckUser(ctx context.Context, in *CheckUserRequest, opts ...grpc.CallOption) (*CheckUserResponse, error)
	DeleteUser(ctx context.Context, in *DeleteUserRequest, opts ...grpc.CallOption) (*DeleteUserResponse, error)
	AddNewData(ctx context.Context, in *AddNewAnswerRequest, opts ...grpc.CallOption) (*AddNewAnswerResponse, error)
	RequestOldDatas(ctx context.Context, in *RequestOldAnswersRequest, opts ...grpc.CallOption) (*RequestOldAnswersResponse, error)
	RequestDeletedDatas(ctx context.Context, in *RequestDeletedAnswersRequest, opts ...grpc.CallOption) (*RequestDeletedAnswersResponse, error)
}

type databaseClient struct {
	cc grpc.ClientConnInterface
}

func NewDatabaseClient(cc grpc.ClientConnInterface) DatabaseClient {
	return &databaseClient{cc}
}

func (c *databaseClient) CreateUser(ctx context.Context, in *CreateUserRequest, opts ...grpc.CallOption) (*CreateUserResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(CreateUserResponse)
	err := c.cc.Invoke(ctx, Database_CreateUser_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) CheckUser(ctx context.Context, in *CheckUserRequest, opts ...grpc.CallOption) (*CheckUserResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(CheckUserResponse)
	err := c.cc.Invoke(ctx, Database_CheckUser_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) DeleteUser(ctx context.Context, in *DeleteUserRequest, opts ...grpc.CallOption) (*DeleteUserResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(DeleteUserResponse)
	err := c.cc.Invoke(ctx, Database_DeleteUser_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) AddNewData(ctx context.Context, in *AddNewAnswerRequest, opts ...grpc.CallOption) (*AddNewAnswerResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(AddNewAnswerResponse)
	err := c.cc.Invoke(ctx, Database_AddNewData_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) RequestOldDatas(ctx context.Context, in *RequestOldAnswersRequest, opts ...grpc.CallOption) (*RequestOldAnswersResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(RequestOldAnswersResponse)
	err := c.cc.Invoke(ctx, Database_RequestOldDatas_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

func (c *databaseClient) RequestDeletedDatas(ctx context.Context, in *RequestDeletedAnswersRequest, opts ...grpc.CallOption) (*RequestDeletedAnswersResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(RequestDeletedAnswersResponse)
	err := c.cc.Invoke(ctx, Database_RequestDeletedDatas_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// DatabaseServer is the server API for Database service.
// All implementations must embed UnimplementedDatabaseServer
// for forward compatibility.
type DatabaseServer interface {
	CreateUser(context.Context, *CreateUserRequest) (*CreateUserResponse, error)
	CheckUser(context.Context, *CheckUserRequest) (*CheckUserResponse, error)
	DeleteUser(context.Context, *DeleteUserRequest) (*DeleteUserResponse, error)
	AddNewData(context.Context, *AddNewAnswerRequest) (*AddNewAnswerResponse, error)
	RequestOldDatas(context.Context, *RequestOldAnswersRequest) (*RequestOldAnswersResponse, error)
	RequestDeletedDatas(context.Context, *RequestDeletedAnswersRequest) (*RequestDeletedAnswersResponse, error)
	mustEmbedUnimplementedDatabaseServer()
}

// UnimplementedDatabaseServer must be embedded to have
// forward compatible implementations.
//
// NOTE: this should be embedded by value instead of pointer to avoid a nil
// pointer dereference when methods are called.
type UnimplementedDatabaseServer struct{}

func (UnimplementedDatabaseServer) CreateUser(context.Context, *CreateUserRequest) (*CreateUserResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method CreateUser not implemented")
}
func (UnimplementedDatabaseServer) CheckUser(context.Context, *CheckUserRequest) (*CheckUserResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method CheckUser not implemented")
}
func (UnimplementedDatabaseServer) DeleteUser(context.Context, *DeleteUserRequest) (*DeleteUserResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method DeleteUser not implemented")
}
func (UnimplementedDatabaseServer) AddNewData(context.Context, *AddNewAnswerRequest) (*AddNewAnswerResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method AddNewData not implemented")
}
func (UnimplementedDatabaseServer) RequestOldDatas(context.Context, *RequestOldAnswersRequest) (*RequestOldAnswersResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RequestOldDatas not implemented")
}
func (UnimplementedDatabaseServer) RequestDeletedDatas(context.Context, *RequestDeletedAnswersRequest) (*RequestDeletedAnswersResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method RequestDeletedDatas not implemented")
}
func (UnimplementedDatabaseServer) mustEmbedUnimplementedDatabaseServer() {}
func (UnimplementedDatabaseServer) testEmbeddedByValue()                  {}

// UnsafeDatabaseServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to DatabaseServer will
// result in compilation errors.
type UnsafeDatabaseServer interface {
	mustEmbedUnimplementedDatabaseServer()
}

func RegisterDatabaseServer(s grpc.ServiceRegistrar, srv DatabaseServer) {
	// If the following call pancis, it indicates UnimplementedDatabaseServer was
	// embedded by pointer and is nil.  This will cause panics if an
	// unimplemented method is ever invoked, so we test this at initialization
	// time to prevent it from happening at runtime later due to I/O.
	if t, ok := srv.(interface{ testEmbeddedByValue() }); ok {
		t.testEmbeddedByValue()
	}
	s.RegisterService(&Database_ServiceDesc, srv)
}

func _Database_CreateUser_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(CreateUserRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).CreateUser(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_CreateUser_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).CreateUser(ctx, req.(*CreateUserRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_CheckUser_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(CheckUserRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).CheckUser(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_CheckUser_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).CheckUser(ctx, req.(*CheckUserRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_DeleteUser_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DeleteUserRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).DeleteUser(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_DeleteUser_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).DeleteUser(ctx, req.(*DeleteUserRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_AddNewData_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(AddNewAnswerRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).AddNewData(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_AddNewData_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).AddNewData(ctx, req.(*AddNewAnswerRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_RequestOldDatas_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(RequestOldAnswersRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).RequestOldDatas(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_RequestOldDatas_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).RequestOldDatas(ctx, req.(*RequestOldAnswersRequest))
	}
	return interceptor(ctx, in, info, handler)
}

func _Database_RequestDeletedDatas_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(RequestDeletedAnswersRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DatabaseServer).RequestDeletedDatas(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Database_RequestDeletedDatas_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DatabaseServer).RequestDeletedDatas(ctx, req.(*RequestDeletedAnswersRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// Database_ServiceDesc is the grpc.ServiceDesc for Database service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var Database_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "database.Database",
	HandlerType: (*DatabaseServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "CreateUser",
			Handler:    _Database_CreateUser_Handler,
		},
		{
			MethodName: "CheckUser",
			Handler:    _Database_CheckUser_Handler,
		},
		{
			MethodName: "DeleteUser",
			Handler:    _Database_DeleteUser_Handler,
		},
		{
			MethodName: "AddNewData",
			Handler:    _Database_AddNewData_Handler,
		},
		{
			MethodName: "RequestOldDatas",
			Handler:    _Database_RequestOldDatas_Handler,
		},
		{
			MethodName: "RequestDeletedDatas",
			Handler:    _Database_RequestDeletedDatas_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "newp/database/database.proto",
}

### .\Backend\manager\contract\database\database_grpc.pb.go END ###

### .\Backend\manager\contract\ml\ml.pb.go BEGIN ###
// Code generated by protoc-gen-go. DO NOT EDIT.
// versions:
// 	protoc-gen-go v1.36.10
// 	protoc        v6.33.1
// source: newp/ml/ml.proto

package ml1

import (
	reflect "reflect"
	sync "sync"
	unsafe "unsafe"

	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
	protoimpl "google.golang.org/protobuf/runtime/protoimpl"
)

const (
	// Verify that this generated code is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(20 - protoimpl.MinVersion)
	// Verify that runtime/protoimpl is sufficiently up-to-date.
	_ = protoimpl.EnforceVersion(protoimpl.MaxVersion - 20)
)

type DetectionRequest struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	QueryId       int64                  `protobuf:"varint,1,opt,name=query_id,json=queryId,proto3" json:"query_id,omitempty"`
	DirPath       string                 `protobuf:"bytes,2,opt,name=dir_path,json=dirPath,proto3" json:"dir_path,omitempty"`
	Targets       []string               `protobuf:"bytes,3,rep,name=targets,proto3" json:"targets,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *DetectionRequest) Reset() {
	*x = DetectionRequest{}
	mi := &file_newp_ml_ml_proto_msgTypes[0]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *DetectionRequest) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*DetectionRequest) ProtoMessage() {}

func (x *DetectionRequest) ProtoReflect() protoreflect.Message {
	mi := &file_newp_ml_ml_proto_msgTypes[0]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use DetectionRequest.ProtoReflect.Descriptor instead.
func (*DetectionRequest) Descriptor() ([]byte, []int) {
	return file_newp_ml_ml_proto_rawDescGZIP(), []int{0}
}

func (x *DetectionRequest) GetQueryId() int64 {
	if x != nil {
		return x.QueryId
	}
	return 0
}

func (x *DetectionRequest) GetDirPath() string {
	if x != nil {
		return x.DirPath
	}
	return ""
}

func (x *DetectionRequest) GetTargets() []string {
	if x != nil {
		return x.Targets
	}
	return nil
}

type DetectionResponse struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	QueryId       int64                  `protobuf:"varint,1,opt,name=query_id,json=queryId,proto3" json:"query_id,omitempty"`
	ResultPath    string                 `protobuf:"bytes,2,opt,name=result_path,json=resultPath,proto3" json:"result_path,omitempty"`
	Success       bool                   `protobuf:"varint,3,opt,name=success,proto3" json:"success,omitempty"`
	InstanceInfo  []*InstanceInfo        `protobuf:"bytes,4,rep,name=instance_info,json=instanceInfo,proto3" json:"instance_info,omitempty"`
	ErrorMessage  string                 `protobuf:"bytes,5,opt,name=error_message,json=errorMessage,proto3" json:"error_message,omitempty"`
	TotalObjects  int32                  `protobuf:"varint,6,opt,name=total_objects,json=totalObjects,proto3" json:"total_objects,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *DetectionResponse) Reset() {
	*x = DetectionResponse{}
	mi := &file_newp_ml_ml_proto_msgTypes[1]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *DetectionResponse) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*DetectionResponse) ProtoMessage() {}

func (x *DetectionResponse) ProtoReflect() protoreflect.Message {
	mi := &file_newp_ml_ml_proto_msgTypes[1]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use DetectionResponse.ProtoReflect.Descriptor instead.
func (*DetectionResponse) Descriptor() ([]byte, []int) {
	return file_newp_ml_ml_proto_rawDescGZIP(), []int{1}
}

func (x *DetectionResponse) GetQueryId() int64 {
	if x != nil {
		return x.QueryId
	}
	return 0
}

func (x *DetectionResponse) GetResultPath() string {
	if x != nil {
		return x.ResultPath
	}
	return ""
}

func (x *DetectionResponse) GetSuccess() bool {
	if x != nil {
		return x.Success
	}
	return false
}

func (x *DetectionResponse) GetInstanceInfo() []*InstanceInfo {
	if x != nil {
		return x.InstanceInfo
	}
	return nil
}

func (x *DetectionResponse) GetErrorMessage() string {
	if x != nil {
		return x.ErrorMessage
	}
	return ""
}

func (x *DetectionResponse) GetTotalObjects() int32 {
	if x != nil {
		return x.TotalObjects
	}
	return 0
}

type InstanceInfo struct {
	state         protoimpl.MessageState `protogen:"open.v1"`
	ClassName     string                 `protobuf:"bytes,1,opt,name=class_name,json=className,proto3" json:"class_name,omitempty"`
	Confidience   float32                `protobuf:"fixed32,2,opt,name=confidience,proto3" json:"confidience,omitempty"`
	Bbox          []float32              `protobuf:"fixed32,3,rep,packed,name=bbox,proto3" json:"bbox,omitempty"`
	unknownFields protoimpl.UnknownFields
	sizeCache     protoimpl.SizeCache
}

func (x *InstanceInfo) Reset() {
	*x = InstanceInfo{}
	mi := &file_newp_ml_ml_proto_msgTypes[2]
	ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
	ms.StoreMessageInfo(mi)
}

func (x *InstanceInfo) String() string {
	return protoimpl.X.MessageStringOf(x)
}

func (*InstanceInfo) ProtoMessage() {}

func (x *InstanceInfo) ProtoReflect() protoreflect.Message {
	mi := &file_newp_ml_ml_proto_msgTypes[2]
	if x != nil {
		ms := protoimpl.X.MessageStateOf(protoimpl.Pointer(x))
		if ms.LoadMessageInfo() == nil {
			ms.StoreMessageInfo(mi)
		}
		return ms
	}
	return mi.MessageOf(x)
}

// Deprecated: Use InstanceInfo.ProtoReflect.Descriptor instead.
func (*InstanceInfo) Descriptor() ([]byte, []int) {
	return file_newp_ml_ml_proto_rawDescGZIP(), []int{2}
}

func (x *InstanceInfo) GetClassName() string {
	if x != nil {
		return x.ClassName
	}
	return ""
}

func (x *InstanceInfo) GetConfidience() float32 {
	if x != nil {
		return x.Confidience
	}
	return 0
}

func (x *InstanceInfo) GetBbox() []float32 {
	if x != nil {
		return x.Bbox
	}
	return nil
}

var File_newp_ml_ml_proto protoreflect.FileDescriptor

const file_newp_ml_ml_proto_rawDesc = "" +
	"\n" +
	"\x10newp/ml/ml.proto\x12\x04grps\"b\n" +
	"\x10DetectionRequest\x12\x19\n" +
	"\bquery_id\x18\x01 \x01(\x03R\aqueryId\x12\x19\n" +
	"\bdir_path\x18\x02 \x01(\tR\adirPath\x12\x18\n" +
	"\atargets\x18\x03 \x03(\tR\atargets\"\xec\x01\n" +
	"\x11DetectionResponse\x12\x19\n" +
	"\bquery_id\x18\x01 \x01(\x03R\aqueryId\x12\x1f\n" +
	"\vresult_path\x18\x02 \x01(\tR\n" +
	"resultPath\x12\x18\n" +
	"\asuccess\x18\x03 \x01(\bR\asuccess\x127\n" +
	"\rinstance_info\x18\x04 \x03(\v2\x12.grps.InstanceInfoR\finstanceInfo\x12#\n" +
	"\rerror_message\x18\x05 \x01(\tR\ferrorMessage\x12#\n" +
	"\rtotal_objects\x18\x06 \x01(\x05R\ftotalObjects\"c\n" +
	"\fInstanceInfo\x12\x1d\n" +
	"\n" +
	"class_name\x18\x01 \x01(\tR\tclassName\x12 \n" +
	"\vconfidience\x18\x02 \x01(\x02R\vconfidience\x12\x12\n" +
	"\x04bbox\x18\x03 \x03(\x02R\x04bbox2M\n" +
	"\bDetector\x12A\n" +
	"\x0eImageDetection\x12\x16.grps.DetectionRequest\x1a\x17.grps.DetectionResponseB\x12Z\x10sirius.ml.v1;ml1b\x06proto3"

var (
	file_newp_ml_ml_proto_rawDescOnce sync.Once
	file_newp_ml_ml_proto_rawDescData []byte
)

func file_newp_ml_ml_proto_rawDescGZIP() []byte {
	file_newp_ml_ml_proto_rawDescOnce.Do(func() {
		file_newp_ml_ml_proto_rawDescData = protoimpl.X.CompressGZIP(unsafe.Slice(unsafe.StringData(file_newp_ml_ml_proto_rawDesc), len(file_newp_ml_ml_proto_rawDesc)))
	})
	return file_newp_ml_ml_proto_rawDescData
}

var file_newp_ml_ml_proto_msgTypes = make([]protoimpl.MessageInfo, 3)
var file_newp_ml_ml_proto_goTypes = []any{
	(*DetectionRequest)(nil),  // 0: grps.DetectionRequest
	(*DetectionResponse)(nil), // 1: grps.DetectionResponse
	(*InstanceInfo)(nil),      // 2: grps.InstanceInfo
}
var file_newp_ml_ml_proto_depIdxs = []int32{
	2, // 0: grps.DetectionResponse.instance_info:type_name -> grps.InstanceInfo
	0, // 1: grps.Detector.ImageDetection:input_type -> grps.DetectionRequest
	1, // 2: grps.Detector.ImageDetection:output_type -> grps.DetectionResponse
	2, // [2:3] is the sub-list for method output_type
	1, // [1:2] is the sub-list for method input_type
	1, // [1:1] is the sub-list for extension type_name
	1, // [1:1] is the sub-list for extension extendee
	0, // [0:1] is the sub-list for field type_name
}

func init() { file_newp_ml_ml_proto_init() }
func file_newp_ml_ml_proto_init() {
	if File_newp_ml_ml_proto != nil {
		return
	}
	type x struct{}
	out := protoimpl.TypeBuilder{
		File: protoimpl.DescBuilder{
			GoPackagePath: reflect.TypeOf(x{}).PkgPath(),
			RawDescriptor: unsafe.Slice(unsafe.StringData(file_newp_ml_ml_proto_rawDesc), len(file_newp_ml_ml_proto_rawDesc)),
			NumEnums:      0,
			NumMessages:   3,
			NumExtensions: 0,
			NumServices:   1,
		},
		GoTypes:           file_newp_ml_ml_proto_goTypes,
		DependencyIndexes: file_newp_ml_ml_proto_depIdxs,
		MessageInfos:      file_newp_ml_ml_proto_msgTypes,
	}.Build()
	File_newp_ml_ml_proto = out.File
	file_newp_ml_ml_proto_goTypes = nil
	file_newp_ml_ml_proto_depIdxs = nil
}

### .\Backend\manager\contract\ml\ml.pb.go END ###

### .\Backend\manager\contract\ml\ml_grpc.pb.go BEGIN ###
// Code generated by protoc-gen-go-grpc. DO NOT EDIT.
// versions:
// - protoc-gen-go-grpc v1.5.1
// - protoc             v6.33.1
// source: newp/ml/ml.proto

package ml1

import (
	context "context"

	grpc "google.golang.org/grpc"
	codes "google.golang.org/grpc/codes"
	status "google.golang.org/grpc/status"
)

// This is a compile-time assertion to ensure that this generated file
// is compatible with the grpc package it is being compiled against.
// Requires gRPC-Go v1.64.0 or later.
const _ = grpc.SupportPackageIsVersion9

const (
	Detector_ImageDetection_FullMethodName = "/grps.Detector/ImageDetection"
)

// DetectorClient is the client API for Detector service.
//
// For semantics around ctx use and closing/ending streaming RPCs, please refer to https://pkg.go.dev/google.golang.org/grpc/?tab=doc#ClientConn.NewStream.
type DetectorClient interface {
	ImageDetection(ctx context.Context, in *DetectionRequest, opts ...grpc.CallOption) (*DetectionResponse, error)
}

type detectorClient struct {
	cc grpc.ClientConnInterface
}

func NewDetectorClient(cc grpc.ClientConnInterface) DetectorClient {
	return &detectorClient{cc}
}

func (c *detectorClient) ImageDetection(ctx context.Context, in *DetectionRequest, opts ...grpc.CallOption) (*DetectionResponse, error) {
	cOpts := append([]grpc.CallOption{grpc.StaticMethod()}, opts...)
	out := new(DetectionResponse)
	err := c.cc.Invoke(ctx, Detector_ImageDetection_FullMethodName, in, out, cOpts...)
	if err != nil {
		return nil, err
	}
	return out, nil
}

// DetectorServer is the server API for Detector service.
// All implementations must embed UnimplementedDetectorServer
// for forward compatibility.
type DetectorServer interface {
	ImageDetection(context.Context, *DetectionRequest) (*DetectionResponse, error)
	mustEmbedUnimplementedDetectorServer()
}

// UnimplementedDetectorServer must be embedded to have
// forward compatible implementations.
//
// NOTE: this should be embedded by value instead of pointer to avoid a nil
// pointer dereference when methods are called.
type UnimplementedDetectorServer struct{}

func (UnimplementedDetectorServer) ImageDetection(context.Context, *DetectionRequest) (*DetectionResponse, error) {
	return nil, status.Errorf(codes.Unimplemented, "method ImageDetection not implemented")
}
func (UnimplementedDetectorServer) mustEmbedUnimplementedDetectorServer() {}
func (UnimplementedDetectorServer) testEmbeddedByValue()                  {}

// UnsafeDetectorServer may be embedded to opt out of forward compatibility for this service.
// Use of this interface is not recommended, as added methods to DetectorServer will
// result in compilation errors.
type UnsafeDetectorServer interface {
	mustEmbedUnimplementedDetectorServer()
}

func RegisterDetectorServer(s grpc.ServiceRegistrar, srv DetectorServer) {
	// If the following call pancis, it indicates UnimplementedDetectorServer was
	// embedded by pointer and is nil.  This will cause panics if an
	// unimplemented method is ever invoked, so we test this at initialization
	// time to prevent it from happening at runtime later due to I/O.
	if t, ok := srv.(interface{ testEmbeddedByValue() }); ok {
		t.testEmbeddedByValue()
	}
	s.RegisterService(&Detector_ServiceDesc, srv)
}

func _Detector_ImageDetection_Handler(srv interface{}, ctx context.Context, dec func(interface{}) error, interceptor grpc.UnaryServerInterceptor) (interface{}, error) {
	in := new(DetectionRequest)
	if err := dec(in); err != nil {
		return nil, err
	}
	if interceptor == nil {
		return srv.(DetectorServer).ImageDetection(ctx, in)
	}
	info := &grpc.UnaryServerInfo{
		Server:     srv,
		FullMethod: Detector_ImageDetection_FullMethodName,
	}
	handler := func(ctx context.Context, req interface{}) (interface{}, error) {
		return srv.(DetectorServer).ImageDetection(ctx, req.(*DetectionRequest))
	}
	return interceptor(ctx, in, info, handler)
}

// Detector_ServiceDesc is the grpc.ServiceDesc for Detector service.
// It's only intended for direct use with grpc.RegisterService,
// and not to be introspected or modified (even as a copy)
var Detector_ServiceDesc = grpc.ServiceDesc{
	ServiceName: "grps.Detector",
	HandlerType: (*DetectorServer)(nil),
	Methods: []grpc.MethodDesc{
		{
			MethodName: "ImageDetection",
			Handler:    _Detector_ImageDetection_Handler,
		},
	},
	Streams:  []grpc.StreamDesc{},
	Metadata: "newp/ml/ml.proto",
}

### .\Backend\manager\contract\ml\ml_grpc.pb.go END ###

### .\Backend\manager\Dockerfile BEGIN ###
FROM golang:1.24-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o /manager ./cmd/main.go

FROM alpine:latest

WORKDIR /app

COPY --from=builder /manager .
COPY config/ config/

RUN mkdir -p volume

EXPOSE 8080

CMD ["./manager", "--config=config/config.yaml"]

### .\Backend\manager\Dockerfile END ###

### .\Backend\manager\go.mod BEGIN ###
module manager

go 1.24.2

require (
	github.com/PrototypeSirius/ruglogger v0.0.0-20260124155947-d30e99226478
	github.com/gin-contrib/cors v1.7.6
	github.com/gin-gonic/gin v1.11.0
	github.com/golang-jwt/jwt/v5 v5.3.1
	github.com/ilyakaznacheev/cleanenv v1.5.0
	golang.org/x/crypto v0.46.0
	google.golang.org/grpc v1.79.1
	google.golang.org/protobuf v1.36.11
)

require (
	github.com/BurntSushi/toml v1.2.1 // indirect
	github.com/bytedance/sonic v1.14.0 // indirect
	github.com/bytedance/sonic/loader v0.3.0 // indirect
	github.com/cloudwego/base64x v0.1.6 // indirect
	github.com/gabriel-vasile/mimetype v1.4.9 // indirect
	github.com/gin-contrib/sse v1.1.0 // indirect
	github.com/go-playground/locales v0.14.1 // indirect
	github.com/go-playground/universal-translator v0.18.1 // indirect
	github.com/go-playground/validator/v10 v10.27.0 // indirect
	github.com/goccy/go-json v0.10.5 // indirect
	github.com/goccy/go-yaml v1.18.0 // indirect
	github.com/gorilla/websocket v1.5.3 // indirect
	github.com/joho/godotenv v1.5.1 // indirect
	github.com/json-iterator/go v1.1.12 // indirect
	github.com/klauspost/cpuid/v2 v2.3.0 // indirect
	github.com/kr/text v0.2.0 // indirect
	github.com/leodido/go-urn v1.4.0 // indirect
	github.com/mattn/go-isatty v0.0.20 // indirect
	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
	github.com/modern-go/reflect2 v1.0.2 // indirect
	github.com/pelletier/go-toml/v2 v2.2.4 // indirect
	github.com/quic-go/qpack v0.5.1 // indirect
	github.com/quic-go/quic-go v0.54.0 // indirect
	github.com/twitchyliquid64/golang-asm v0.15.1 // indirect
	github.com/ugorji/go/codec v1.3.0 // indirect
	go.uber.org/mock v0.5.0 // indirect
	golang.org/x/arch v0.20.0 // indirect
	golang.org/x/mod v0.30.0 // indirect
	golang.org/x/net v0.48.0 // indirect
	golang.org/x/sync v0.19.0 // indirect
	golang.org/x/sys v0.39.0 // indirect
	golang.org/x/text v0.32.0 // indirect
	golang.org/x/tools v0.39.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217 // indirect
	gopkg.in/yaml.v3 v3.0.1 // indirect
	olympos.io/encoding/edn v0.0.0-20201019073823-d3554ca0b0a3 // indirect
)

### .\Backend\manager\go.mod END ###

### .\Backend\manager\go.sum BEGIN ###
github.com/BurntSushi/toml v1.2.1 h1:9F2/+DoOYIOksmaJFPw1tGFy1eDnIJXg+UHjuD8lTak=
github.com/BurntSushi/toml v1.2.1/go.mod h1:CxXYINrC8qIiEnFrOxCa7Jy5BFHlXnUU2pbicEuybxQ=
github.com/PrototypeSirius/ruglogger v0.0.0-20260124155947-d30e99226478 h1:1saj4+qX1UccPw6ZKB4FVG+uzGm47OTGHur6ohLbGFo=
github.com/PrototypeSirius/ruglogger v0.0.0-20260124155947-d30e99226478/go.mod h1:Gpp4OyX1d/1u7csaTbgA7OArFj/AfIoBFntLeb3VCY8=
github.com/bytedance/sonic v1.14.0 h1:/OfKt8HFw0kh2rj8N0F6C/qPGRESq0BbaNZgcNXXzQQ=
github.com/bytedance/sonic v1.14.0/go.mod h1:WoEbx8WTcFJfzCe0hbmyTGrfjt8PzNEBdxlNUO24NhA=
github.com/bytedance/sonic/loader v0.3.0 h1:dskwH8edlzNMctoruo8FPTJDF3vLtDT0sXZwvZJyqeA=
github.com/bytedance/sonic/loader v0.3.0/go.mod h1:N8A3vUdtUebEY2/VQC0MyhYeKUFosQU6FxH2JmUe6VI=
github.com/cespare/xxhash/v2 v2.3.0 h1:UL815xU9SqsFlibzuggzjXhog7bL6oX9BbNZnL2UFvs=
github.com/cespare/xxhash/v2 v2.3.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
github.com/cloudwego/base64x v0.1.6 h1:t11wG9AECkCDk5fMSoxmufanudBtJ+/HemLstXDLI2M=
github.com/cloudwego/base64x v0.1.6/go.mod h1:OFcloc187FXDaYHvrNIjxSe8ncn0OOM8gEHfghB2IPU=
github.com/creack/pty v1.1.9/go.mod h1:oKZEueFk5CKHvIhNR5MUki03XCEU+Q6VDXinZuGJ33E=
github.com/davecgh/go-spew v1.1.0/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/davecgh/go-spew v1.1.1 h1:vj9j/u1bqnvCEfJOwUhtlOARqs3+rkHYY13jYWTU97c=
github.com/davecgh/go-spew v1.1.1/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
github.com/gabriel-vasile/mimetype v1.4.9 h1:5k+WDwEsD9eTLL8Tz3L0VnmVh9QxGjRmjBvAG7U/oYY=
github.com/gabriel-vasile/mimetype v1.4.9/go.mod h1:WnSQhFKJuBlRyLiKohA/2DtIlPFAbguNaG7QCHcyGok=
github.com/gin-contrib/cors v1.7.6 h1:3gQ8GMzs1Ylpf70y8bMw4fVpycXIeX1ZemuSQIsnQQY=
github.com/gin-contrib/cors v1.7.6/go.mod h1:Ulcl+xN4jel9t1Ry8vqph23a60FwH9xVLd+3ykmTjOk=
github.com/gin-contrib/sse v1.1.0 h1:n0w2GMuUpWDVp7qSpvze6fAu9iRxJY4Hmj6AmBOU05w=
github.com/gin-contrib/sse v1.1.0/go.mod h1:hxRZ5gVpWMT7Z0B0gSNYqqsSCNIJMjzvm6fqCz9vjwM=
github.com/gin-gonic/gin v1.11.0 h1:OW/6PLjyusp2PPXtyxKHU0RbX6I/l28FTdDlae5ueWk=
github.com/gin-gonic/gin v1.11.0/go.mod h1:+iq/FyxlGzII0KHiBGjuNn4UNENUlKbGlNmc+W50Dls=
github.com/go-logr/logr v1.4.3 h1:CjnDlHq8ikf6E492q6eKboGOC0T8CDaOvkHCIg8idEI=
github.com/go-logr/logr v1.4.3/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
github.com/go-logr/stdr v1.2.2 h1:hSWxHoqTgW2S2qGc0LTAI563KZ5YKYRhT3MFKZMbjag=
github.com/go-logr/stdr v1.2.2/go.mod h1:mMo/vtBO5dYbehREoey6XUKy/eSumjCCveDpRre4VKE=
github.com/go-playground/assert/v2 v2.2.0 h1:JvknZsQTYeFEAhQwI4qEt9cyV5ONwRHC+lYKSsYSR8s=
github.com/go-playground/assert/v2 v2.2.0/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
github.com/go-playground/locales v0.14.1 h1:EWaQ/wswjilfKLTECiXz7Rh+3BjFhfDFKv/oXslEjJA=
github.com/go-playground/locales v0.14.1/go.mod h1:hxrqLVvrK65+Rwrd5Fc6F2O76J/NuW9t0sjnWqG1slY=
github.com/go-playground/universal-translator v0.18.1 h1:Bcnm0ZwsGyWbCzImXv+pAJnYK9S473LQFuzCbDbfSFY=
github.com/go-playground/universal-translator v0.18.1/go.mod h1:xekY+UJKNuX9WP91TpwSH2VMlDf28Uj24BCp08ZFTUY=
github.com/go-playground/validator/v10 v10.27.0 h1:w8+XrWVMhGkxOaaowyKH35gFydVHOvC0/uWoy2Fzwn4=
github.com/go-playground/validator/v10 v10.27.0/go.mod h1:I5QpIEbmr8On7W0TktmJAumgzX4CA1XNl4ZmDuVHKKo=
github.com/goccy/go-json v0.10.5 h1:Fq85nIqj+gXn/S5ahsiTlK3TmC85qgirsdTP/+DeaC4=
github.com/goccy/go-json v0.10.5/go.mod h1:oq7eo15ShAhp70Anwd5lgX2pLfOS3QCiwU/PULtXL6M=
github.com/goccy/go-yaml v1.18.0 h1:8W7wMFS12Pcas7KU+VVkaiCng+kG8QiFeFwzFb+rwuw=
github.com/goccy/go-yaml v1.18.0/go.mod h1:XBurs7gK8ATbW4ZPGKgcbrY1Br56PdM69F7LkFRi1kA=
github.com/golang-jwt/jwt/v5 v5.3.1 h1:kYf81DTWFe7t+1VvL7eS+jKFVWaUnK9cB1qbwn63YCY=
github.com/golang-jwt/jwt/v5 v5.3.1/go.mod h1:fxCRLWMO43lRc8nhHWY6LGqRcf+1gQWArsqaEUEa5bE=
github.com/golang/protobuf v1.5.4 h1:i7eJL8qZTpSEXOPTxNKhASYpMn+8e5Q6AdndVa1dWek=
github.com/golang/protobuf v1.5.4/go.mod h1:lnTiLA8Wa4RWRcIUkrtSVa5nRhsEGBg48fD6rSs7xps=
github.com/google/go-cmp v0.7.0 h1:wk8382ETsv4JYUZwIsn6YpYiWiBsYLSJiTsyBybVuN8=
github.com/google/go-cmp v0.7.0/go.mod h1:pXiqmnSA92OHEEa9HXL2W4E7lf9JzCmGVUdgjX3N/iU=
github.com/google/gofuzz v1.0.0/go.mod h1:dBl0BpW6vV/+mYPU4Po3pmUjxk6FQPldtuIdl/M65Eg=
github.com/google/uuid v1.6.0 h1:NIvaJDMOsjHA8n1jAhLSgzrAzy1Hgr+hNrb57e+94F0=
github.com/google/uuid v1.6.0/go.mod h1:TIyPZe4MgqvfeYDBFedMoGGpEw/LqOeaOT+nhxU+yHo=
github.com/gorilla/websocket v1.5.3 h1:saDtZ6Pbx/0u+bgYQ3q96pZgCzfhKXGPqt7kZ72aNNg=
github.com/gorilla/websocket v1.5.3/go.mod h1:YR8l580nyteQvAITg2hZ9XVh4b55+EU/adAjf1fMHhE=
github.com/ilyakaznacheev/cleanenv v1.5.0 h1:0VNZXggJE2OYdXE87bfSSwGxeiGt9moSR2lOrsHHvr4=
github.com/ilyakaznacheev/cleanenv v1.5.0/go.mod h1:a5aDzaJrLCQZsazHol1w8InnDcOX0OColm64SlIi6gk=
github.com/joho/godotenv v1.5.1 h1:7eLL/+HRGLY0ldzfGMeQkb7vMd0as4CfYvUVzLqw0N0=
github.com/joho/godotenv v1.5.1/go.mod h1:f4LDr5Voq0i2e/R5DDNOoa2zzDfwtkZa6DnEwAbqwq4=
github.com/json-iterator/go v1.1.12 h1:PV8peI4a0ysnczrg+LtxykD8LfKY9ML6u2jnxaEnrnM=
github.com/json-iterator/go v1.1.12/go.mod h1:e30LSqwooZae/UwlEbR2852Gd8hjQvJoHmT4TnhNGBo=
github.com/klauspost/cpuid/v2 v2.3.0 h1:S4CRMLnYUhGeDFDqkGriYKdfoFlDnMtqTiI/sFzhA9Y=
github.com/klauspost/cpuid/v2 v2.3.0/go.mod h1:hqwkgyIinND0mEev00jJYCxPNVRVXFQeu1XKlok6oO0=
github.com/kr/pretty v0.3.0 h1:WgNl7dwNpEZ6jJ9k1snq4pZsg7DOEN8hP9Xw0Tsjwk0=
github.com/kr/pretty v0.3.0/go.mod h1:640gp4NfQd8pI5XOwp5fnNeVWj67G7CFk/SaSQn7NBk=
github.com/kr/text v0.2.0 h1:5Nx0Ya0ZqY2ygV366QzturHI13Jq95ApcVaJBhpS+AY=
github.com/kr/text v0.2.0/go.mod h1:eLer722TekiGuMkidMxC/pM04lWEeraHUUmBw8l2grE=
github.com/leodido/go-urn v1.4.0 h1:WT9HwE9SGECu3lg4d/dIA+jxlljEa1/ffXKmRjqdmIQ=
github.com/leodido/go-urn v1.4.0/go.mod h1:bvxc+MVxLKB4z00jd1z+Dvzr47oO32F/QSNjSBOlFxI=
github.com/mattn/go-isatty v0.0.20 h1:xfD0iDuEKnDkl03q4limB+vH+GxLEtL/jb4xVJSWWEY=
github.com/mattn/go-isatty v0.0.20/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
github.com/modern-go/concurrent v0.0.0-20180228061459-e0a39a4cb421/go.mod h1:6dJC0mAP4ikYIbvyc7fijjWJddQyLn8Ig3JB5CqoB9Q=
github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd h1:TRLaZ9cD/w8PVh93nsPXa1VrQ6jlwL5oN8l14QlcNfg=
github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd/go.mod h1:6dJC0mAP4ikYIbvyc7fijjWJddQyLn8Ig3JB5CqoB9Q=
github.com/modern-go/reflect2 v1.0.2 h1:xBagoLtFs94CBntxluKeaWgTMpvLxC4ur3nMaC9Gz0M=
github.com/modern-go/reflect2 v1.0.2/go.mod h1:yWuevngMOJpCy52FWWMvUC8ws7m/LJsjYzDa0/r8luk=
github.com/pelletier/go-toml/v2 v2.2.4 h1:mye9XuhQ6gvn5h28+VilKrrPoQVanw5PMw/TB0t5Ec4=
github.com/pelletier/go-toml/v2 v2.2.4/go.mod h1:2gIqNv+qfxSVS7cM2xJQKtLSTLUE9V8t9Stt+h56mCY=
github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
github.com/quic-go/qpack v0.5.1 h1:giqksBPnT/HDtZ6VhtFKgoLOWmlyo9Ei6u9PqzIMbhI=
github.com/quic-go/qpack v0.5.1/go.mod h1:+PC4XFrEskIVkcLzpEkbLqq1uCoxPhQuvK5rH1ZgaEg=
github.com/quic-go/quic-go v0.54.0 h1:6s1YB9QotYI6Ospeiguknbp2Znb/jZYjZLRXn9kMQBg=
github.com/quic-go/quic-go v0.54.0/go.mod h1:e68ZEaCdyviluZmy44P6Iey98v/Wfz6HCjQEm+l8zTY=
github.com/rogpeppe/go-internal v1.8.0 h1:FCbCCtXNOY3UtUuHUYaghJg4y7Fd14rXifAYUAtL9R8=
github.com/rogpeppe/go-internal v1.8.0/go.mod h1:WmiCO8CzOY8rg0OYDC4/i/2WRWAB6poM+XZ2dLUbcbE=
github.com/stretchr/objx v0.1.0/go.mod h1:HFkY916IF+rwdDfMAkV7OtwuqBVzrE8GR6GFx+wExME=
github.com/stretchr/objx v0.4.0/go.mod h1:YvHI0jy2hoMjB+UWwv71VJQ9isScKT/TqJzVSSt89Yw=
github.com/stretchr/objx v0.5.0/go.mod h1:Yh+to48EsGEfYuaHDzXPcE3xhTkx73EhmCGUpEOglKo=
github.com/stretchr/testify v1.3.0/go.mod h1:M5WIy9Dh21IEIfnGCwXGc5bZfKNJtfHm1UVUgZn+9EI=
github.com/stretchr/testify v1.7.1/go.mod h1:6Fq8oRcR53rry900zMqJjRRixrwX3KX962/h/Wwjteg=
github.com/stretchr/testify v1.8.0/go.mod h1:yNjHg4UonilssWZ8iaSj1OCr/vHnekPRkoO+kdMU+MU=
github.com/stretchr/testify v1.8.1/go.mod h1:w2LPCIKwWwSfY2zedu0+kehJoqGctiVI29o6fzry7u4=
github.com/stretchr/testify v1.11.1 h1:7s2iGBzp5EwR7/aIZr8ao5+dra3wiQyKjjFuvgVKu7U=
github.com/stretchr/testify v1.11.1/go.mod h1:wZwfW3scLgRK+23gO65QZefKpKQRnfz6sD981Nm4B6U=
github.com/twitchyliquid64/golang-asm v0.15.1 h1:SU5vSMR7hnwNxj24w34ZyCi/FmDZTkS4MhqMhdFk5YI=
github.com/twitchyliquid64/golang-asm v0.15.1/go.mod h1:a1lVb/DtPvCB8fslRZhAngC2+aY1QWCk3Cedj/Gdt08=
github.com/ugorji/go/codec v1.3.0 h1:Qd2W2sQawAfG8XSvzwhBeoGq71zXOC/Q1E9y/wUcsUA=
github.com/ugorji/go/codec v1.3.0/go.mod h1:pRBVtBSKl77K30Bv8R2P+cLSGaTtex6fsA2Wjqmfxj4=
go.opentelemetry.io/auto/sdk v1.2.1 h1:jXsnJ4Lmnqd11kwkBV2LgLoFMZKizbCi5fNZ/ipaZ64=
go.opentelemetry.io/auto/sdk v1.2.1/go.mod h1:KRTj+aOaElaLi+wW1kO/DZRXwkF4C5xPbEe3ZiIhN7Y=
go.opentelemetry.io/otel v1.39.0 h1:8yPrr/S0ND9QEfTfdP9V+SiwT4E0G7Y5MO7p85nis48=
go.opentelemetry.io/otel v1.39.0/go.mod h1:kLlFTywNWrFyEdH0oj2xK0bFYZtHRYUdv1NklR/tgc8=
go.opentelemetry.io/otel/metric v1.39.0 h1:d1UzonvEZriVfpNKEVmHXbdf909uGTOQjA0HF0Ls5Q0=
go.opentelemetry.io/otel/metric v1.39.0/go.mod h1:jrZSWL33sD7bBxg1xjrqyDjnuzTUB0x1nBERXd7Ftcs=
go.opentelemetry.io/otel/sdk v1.39.0 h1:nMLYcjVsvdui1B/4FRkwjzoRVsMK8uL/cj0OyhKzt18=
go.opentelemetry.io/otel/sdk v1.39.0/go.mod h1:vDojkC4/jsTJsE+kh+LXYQlbL8CgrEcwmt1ENZszdJE=
go.opentelemetry.io/otel/sdk/metric v1.39.0 h1:cXMVVFVgsIf2YL6QkRF4Urbr/aMInf+2WKg+sEJTtB8=
go.opentelemetry.io/otel/sdk/metric v1.39.0/go.mod h1:xq9HEVH7qeX69/JnwEfp6fVq5wosJsY1mt4lLfYdVew=
go.opentelemetry.io/otel/trace v1.39.0 h1:2d2vfpEDmCJ5zVYz7ijaJdOF59xLomrvj7bjt6/qCJI=
go.opentelemetry.io/otel/trace v1.39.0/go.mod h1:88w4/PnZSazkGzz/w84VHpQafiU4EtqqlVdxWy+rNOA=
go.uber.org/mock v0.5.0 h1:KAMbZvZPyBPWgD14IrIQ38QCyjwpvVVV6K/bHl1IwQU=
go.uber.org/mock v0.5.0/go.mod h1:ge71pBPLYDk7QIi1LupWxdAykm7KIEFchiOqd6z7qMM=
golang.org/x/arch v0.20.0 h1:dx1zTU0MAE98U+TQ8BLl7XsJbgze2WnNKF/8tGp/Q6c=
golang.org/x/arch v0.20.0/go.mod h1:bdwinDaKcfZUGpH09BB7ZmOfhalA8lQdzl62l8gGWsk=
golang.org/x/crypto v0.46.0 h1:cKRW/pmt1pKAfetfu+RCEvjvZkA9RimPbh7bhFjGVBU=
golang.org/x/crypto v0.46.0/go.mod h1:Evb/oLKmMraqjZ2iQTwDwvCtJkczlDuTmdJXoZVzqU0=
golang.org/x/mod v0.30.0 h1:fDEXFVZ/fmCKProc/yAXXUijritrDzahmwwefnjoPFk=
golang.org/x/mod v0.30.0/go.mod h1:lAsf5O2EvJeSFMiBxXDki7sCgAxEUcZHXoXMKT4GJKc=
golang.org/x/net v0.48.0 h1:zyQRTTrjc33Lhh0fBgT/H3oZq9WuvRR5gPC70xpDiQU=
golang.org/x/net v0.48.0/go.mod h1:+ndRgGjkh8FGtu1w1FGbEC31if4VrNVMuKTgcAAnQRY=
golang.org/x/sync v0.19.0 h1:vV+1eWNmZ5geRlYjzm2adRgW2/mcpevXNg50YZtPCE4=
golang.org/x/sync v0.19.0/go.mod h1:9KTHXmSnoGruLpwFjVSX0lNNA75CykiMECbovNTZqGI=
golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
golang.org/x/sys v0.39.0 h1:CvCKL8MeisomCi6qNZ+wbb0DN9E5AATixKsvNtMoMFk=
golang.org/x/sys v0.39.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
golang.org/x/text v0.32.0 h1:ZD01bjUt1FQ9WJ0ClOL5vxgxOI/sVCNgX1YtKwcY0mU=
golang.org/x/text v0.32.0/go.mod h1:o/rUWzghvpD5TXrTIBuJU77MTaN0ljMWE47kxGJQ7jY=
golang.org/x/tools v0.39.0 h1:ik4ho21kwuQln40uelmciQPp9SipgNDdrafrYA4TmQQ=
golang.org/x/tools v0.39.0/go.mod h1:JnefbkDPyD8UU2kI5fuf8ZX4/yUeh9W877ZeBONxUqQ=
gonum.org/v1/gonum v0.16.0 h1:5+ul4Swaf3ESvrOnidPp4GZbzf0mxVQpDCYUQE7OJfk=
gonum.org/v1/gonum v0.16.0/go.mod h1:fef3am4MQ93R2HHpKnLk4/Tbh/s0+wqD5nfa6Pnwy4E=
google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217 h1:gRkg/vSppuSQoDjxyiGfN4Upv/h/DQmIR10ZU8dh4Ww=
google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217/go.mod h1:7i2o+ce6H/6BluujYR+kqX3GKH+dChPTQU19wjRPiGk=
google.golang.org/grpc v1.79.1 h1:zGhSi45ODB9/p3VAawt9a+O/MULLl9dpizzNNpq7flY=
google.golang.org/grpc v1.79.1/go.mod h1:KmT0Kjez+0dde/v2j9vzwoAScgEPx/Bw1CYChhHLrHQ=
google.golang.org/protobuf v1.36.11 h1:fV6ZwhNocDyBLK0dj+fg8ektcVegBBuEolpbTQyBNVE=
google.golang.org/protobuf v1.36.11/go.mod h1:HTf+CrKn2C3g5S8VImy6tdcUvCska2kB7j23XfzDpco=
gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405/go.mod h1:Co6ibVJAznAaIkqp8huTwlJQCZ016jof/cbN4VW5Yz0=
gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c h1:Hei/4ADfdWqJk1ZMxUNpqntNwaWcugrBjAiHlqqRiVk=
gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c/go.mod h1:JHkPIbrfpd72SG/EVd6muEfDQjcINNoR0C8j2r3qZ4Q=
gopkg.in/yaml.v3 v3.0.0-20200313102051-9f266ea9e77c/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
olympos.io/encoding/edn v0.0.0-20201019073823-d3554ca0b0a3 h1:slmdOY3vp8a7KQbHkL+FLbvbkgMqmXojpFUO/jENuqQ=
olympos.io/encoding/edn v0.0.0-20201019073823-d3554ca0b0a3/go.mod h1:oVgVk4OWVDi43qWBEyGhXgYxt7+ED4iYNpTngSLX2Iw=

### .\Backend\manager\go.sum END ###

### .\Backend\manager\internal\app\app.go BEGIN ###
package app

import (
	httpapp "manager/internal/app/http"
	"manager/internal/config"
	dbclient "manager/internal/repository/database"
	mlclient "manager/internal/repository/ml"
	"manager/internal/router"
	httpservices "manager/internal/services"
	"strconv"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type App struct {
	HTTPApp *httpapp.HTTPApp
	dbConn  *grpc.ClientConn
	mlConn  *grpc.ClientConn
}

func New(cfg *config.Config) *App {
	// Initialize gRPC Connections
	dbTarget := cfg.Client.Database.Host + ":" + strconv.Itoa(cfg.Client.Database.Port)
	dbConn, err := grpc.NewClient(dbTarget, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		panic("failed to connect to DB service: " + err.Error())
	}
	dbCli := dbclient.NewClient(dbConn)

	mlTarget := cfg.Client.ML.Host + ":" + strconv.Itoa(cfg.Client.ML.Port)
	mlConn, err := grpc.NewClient(mlTarget, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		panic("failed to connect to ML service: " + err.Error())
	}
	mlCli := mlclient.NewClient(mlConn)

	// Build Business Layer
	httpService := httpservices.New(dbCli, mlCli, cfg.JWTSecret, cfg.TempObjectPath)

	// Configure HTTP Core Server
	http := httpapp.New(cfg.HttpServer.Port)

	// Delegate routing registration
	router.RouterRegister(http.GetEngine(), httpService, cfg.TempObjectPath)

	return &App{
		HTTPApp: http,
		dbConn:  dbConn,
		mlConn:  mlConn,
	}
}

// Close ensures the graceful termination of associated dialers.
func (a *App) Close() {
	if a.dbConn != nil {
		a.dbConn.Close()
	}
	if a.mlConn != nil {
		a.mlConn.Close()
	}
}

### .\Backend\manager\internal\app\app.go END ###

### .\Backend\manager\internal\app\http\app.go BEGIN ###
package httpapp

// Error code: 2500

import (
	"fmt"

	"github.com/PrototypeSirius/ruglogger/middleware"
	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type HTTPApp struct {
	ginServer *gin.Engine
	port      int
}

func New(port int) *HTTPApp {
	gin.ForceConsoleColor()
	r := gin.New()
	r.Use(gin.Logger())
	r.Use(gin.Recovery())
	r.Use(middleware.StructuredLogHandler())
	r.Use(middleware.ErrorHandler())
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"}, // Modified for universal local access
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept", "Authorization"},
		ExposeHeaders:    []string{"Content-Length", "Authorization"},
		AllowCredentials: true,
	}))
	return &HTTPApp{
		ginServer: r,
		port:      port,
	}
}

func (a *HTTPApp) GetEngine() *gin.Engine {
	return a.ginServer
}

func (a *HTTPApp) MustRun() {
	if err := a.Run(); err != nil {
		logger.Fatal("Failed to run http server", err, 2501, nil)
	}
}

func (a *HTTPApp) Run() error {
	addr := fmt.Sprintf(":%d", a.port)
	logger.Info("HTTP server is running", map[string]any{"address": addr})
	if err := a.ginServer.Run(addr); err != nil {
		return err
	}
	return nil
}

### .\Backend\manager\internal\app\http\app.go END ###

### .\Backend\manager\internal\config\config.go BEGIN ###
package config

import (
	"flag"
	"os"
	"time"

	logger "github.com/PrototypeSirius/ruglogger/ruglog"
	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	Env            string       `yaml:"env" env-default:"local"`               // debug, local, test, production
	FormatTime     string       `yaml:"format_time" env-default:"RFC3339"`     // time format
	LogFilePath    string       `yaml:"log_file_path" env-default:"app.log"`   // log file path
	TempObjectPath string       `yaml:"temp_object_path" env-default:"volume"` // temp object path
	JWTSecret      string       `yaml:"jwt_secret" env-default:"secret"`
	HttpServer     HttpConfig   `yaml:"httpserver"` // http server config
	Client         ClientConfig `yaml:"client"`     // client config
}

type ClientConfig struct {
	Database HttpConfig `yaml:"database"` // database client config
	ML       HttpConfig `yaml:"ml"`       // ml client config
}

type HttpConfig struct {
	Port int    `yaml:"port" env-required:"true"` // HTTP port
	Host string `yaml:"host" env-required:"true"` // HTTP host
}

var level logger.Level

var timeLayouts = map[string]string{
	"Layout":      time.Layout,
	"ANSIC":       time.ANSIC,
	"UnixDate":    time.UnixDate,
	"RubyDate":    time.RubyDate,
	"RFC822":      time.RFC822,
	"RFC822Z":     time.RFC822Z,
	"RFC850":      time.RFC850,
	"RFC1123":     time.RFC1123,
	"RFC1123Z":    time.RFC1123Z,
	"RFC3339":     time.RFC3339,
	"RFC3339Nano": time.RFC3339Nano,
	"Kitchen":     time.Kitchen,
	"Stamp":       time.Stamp,
	"StampMilli":  time.StampMilli,
	"StampMicro":  time.StampMicro,
	"StampNano":   time.StampNano,
	"DataTime":    time.DateTime,
	"DataOnly":    time.DateOnly,
	"TimeOnly":    time.TimeOnly,
}

func getTimeLayout(configValue string) string {
	if layout, ok := timeLayouts[configValue]; ok {
		return layout
	}
	return time.RFC3339
}

func relevel(l string) logger.Level {
	if l == "" {
		l = "local"
	}
	switch l {
	case "debug":
		level = logger.LevelDebug
	case "local":
		level = logger.LevelInfo
	case "test":
		level = logger.LevelWarn
	case "production":
		level = logger.LevelError
	}
	return level
}

func MustLoad() (*Config, logger.Level) {
	path := fechPathConfig()
	if path == "" {
		panic("config path is empty")
	}
	if _, err := os.Stat(path); os.IsNotExist(err) {
		panic("config file not found: " + path)
	}
	var cfg Config
	if err := cleanenv.ReadConfig(path, &cfg); err != nil {
		panic("failed to load config: " + err.Error())
	}
	cfg.FormatTime = getTimeLayout(cfg.FormatTime)
	return &cfg, relevel(cfg.Env)
}

func fechPathConfig() string {
	var res string
	//--config="path/to/config.yaml"
	flag.StringVar(&res, "config", "", "path to config file")
	flag.Parse()
	return res
}

### .\Backend\manager\internal\config\config.go END ###

### .\Backend\manager\internal\models\models.go BEGIN ###
package models

type AuthRequest struct {
	Login    string `json:"login" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type User struct {
	ID           string `json:"id"`
	Login        string `json:"login"`
	PasswordHash string `json:"password_hash"`
}

type AuthResponse struct {
	Token string `json:"token"`
}

type DetectPayload struct {
	Targets []string `json:"targets"`
}

type HistoryAnswer struct {
	Quantity int64  `json:"quantity"`
	Flag     string `json:"flag"`
}

type HistoryResponse struct {
	QueryId int32         `json:"query_id"`
	Entries []ReportEntry `json:"entries"`
}

type Detection struct {
	Class      string    `json:"class"`
	Confidence float64   `json:"confidence"`
	BBox       []float64 `json:"bbox"`
}
type ReportEntry struct {
	Filename   string      `json:"filename"`
	Detections []Detection `json:"detections"`
}

### .\Backend\manager\internal\models\models.go END ###

### .\Backend\manager\internal\repository\database\client.go BEGIN ###
package dbclientt

import (
	"context"
	"encoding/json"
	"fmt"
	database1 "manager/contract/database"
	"manager/internal/models"
	"strconv"

	"google.golang.org/grpc"
)

type Client struct {
	api database1.DatabaseClient
}

func NewClient(cc grpc.ClientConnInterface) *Client {
	return &Client{api: database1.NewDatabaseClient(cc)}
}

func (c *Client) CreateUser(ctx context.Context, user models.User) error {
	data, _ := json.Marshal(user)
	_, err := c.api.CreateUser(ctx, &database1.CreateUserRequest{
		Data: data,
	})
	return err
}

func (c *Client) GetUserByLogin(ctx context.Context, login string) (models.User, error) {
	reqData, _ := json.Marshal(map[string]string{"login": login})
	resp, err := c.api.CheckUser(ctx, &database1.CheckUserRequest{Data: reqData})
	if err != nil {
		return models.User{}, err
	}

	var user models.User
	if err := json.Unmarshal(resp.Data, &user); err != nil {
		return models.User{}, err
	}
	return user, nil
}

func (c *Client) CreateQuery(ctx context.Context, userID string) (int64, error) {
	reqData, _ := json.Marshal(map[string]string{"user_id": userID})
	resp, err := c.api.AddNewData(ctx, &database1.AddNewAnswerRequest{Data: reqData})
	if err != nil {
		return 0, err
	}

	queryID, err := strconv.ParseInt(resp.Message, 10, 64)
	if err != nil {
		return 0, err
	}
	return queryID, nil
}

func (c *Client) GetHistoryAnswers(ctx context.Context, quantity int64, userID, flag string) ([]int32, error) {
	reqData, _ := c.api.RequestOldDatas(ctx, &database1.RequestOldAnswersRequest{
		Quantity: quantity,
		UserID:   userID,
		Flag:     flag,
	})
	if reqData.Message != "Success" {
		return nil, fmt.Errorf("failed to get history answers: %s", reqData.Message)
	}
	var answers []int32
	if err := json.Unmarshal(reqData.Data, &answers); err != nil {
		return nil, err
	}
	return answers, nil
}

### .\Backend\manager\internal\repository\database\client.go END ###

### .\Backend\manager\internal\repository\ml\client.go BEGIN ###
package mlclient

import (
	"context"
	ml1 "manager/contract/ml"

	"google.golang.org/grpc"
)

type Client struct {
	api ml1.DetectorClient
}

func NewClient(cc grpc.ClientConnInterface) *Client {
	return &Client{api: ml1.NewDetectorClient(cc)}
}

func (c *Client) Detect(ctx context.Context, queryID int64, dirPath string, targets []string) (*ml1.DetectionResponse, error) {
	return c.api.ImageDetection(ctx, &ml1.DetectionRequest{
		QueryId: queryID,
		DirPath: dirPath,
		Targets: targets,
	})
}

### .\Backend\manager\internal\repository\ml\client.go END ###

### .\Backend\manager\internal\router\router.go BEGIN ###
package router

import (
	httpservices "manager/internal/services"
	"net/http"

	"github.com/gin-gonic/gin"
)

func RouterRegister(r *gin.Engine, svc *httpservices.HTTPService, volumePath string) {
	r.GET("/health", func(c *gin.Context) { c.String(http.StatusOK, "OK") })

	v1 := r.Group("/api/v1")
	{
		auth := v1.Group("/auth")
		{
			auth.POST("/register", svc.Register)
			auth.POST("/login", svc.Login)
		}

		protected := v1.Group("/")
		protected.Use(svc.AuthMiddleware())
		{
			protected.POST("/detect", svc.Detect)
			protected.POST("/history", svc.History)
		}
	}

	// Frontend usage: GET /results/{query_id}/result/i.jpg
	r.StaticFS("/results", gin.Dir(volumePath, false))
}

### .\Backend\manager\internal\router\router.go END ###

### .\Backend\manager\internal\services\http.go BEGIN ###
package httpservices

import (
	"bufio"
	"encoding/json"
	"fmt"
	"manager/internal/models"
	dbclientt "manager/internal/repository/database"
	mlclient "manager/internal/repository/ml"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

type HTTPService struct {
	dbClient   *dbclientt.Client
	mlClient   *mlclient.Client
	jwtSecret  []byte
	volumePath string
}

func New(db *dbclientt.Client, ml *mlclient.Client, secret string, volumePath string) *HTTPService {
	return &HTTPService{
		dbClient:   db,
		mlClient:   ml,
		jwtSecret:  []byte(secret),
		volumePath: volumePath,
	}
}

func (s *HTTPService) Register(c *gin.Context) {
	var req models.AuthRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	hash, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	user := models.User{
		Login:        req.Login,
		PasswordHash: string(hash),
	}

	if err := s.dbClient.CreateUser(c.Request.Context(), user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register user (likely exists)"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "User registered successfully"})
}

func (s *HTTPService) Login(c *gin.Context) {
	var req models.AuthRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	user, err := s.dbClient.GetUserByLogin(c.Request.Context(), req.Login)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
		"user_id": user.ID,
		"exp":     time.Now().Add(72 * time.Hour).Unix(),
	})

	tokenString, err := token.SignedString(s.jwtSecret)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusOK, models.AuthResponse{Token: tokenString})
}

func (s *HTTPService) Detect(c *gin.Context) {
	userID := c.GetString("user_id")

	form, err := c.MultipartForm()
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Failed to parse multipart data",
			"details": err.Error(),
		})
		return
	}

	payloadValues := form.Value["payload"]
	if len(payloadValues) == 0 || payloadValues[0] == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Missing 'payload' field in form data"})
		return
	}

	payloadStr := payloadValues[0]

	var payload models.DetectPayload
	if err := json.Unmarshal([]byte(payloadStr), &payload); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid JSON in 'payload' field",
			"details": err.Error(),
		})
		return
	}

	queryID, err := s.dbClient.CreateQuery(c.Request.Context(), userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to register query task"})
		return
	}

	queryStrID := strconv.FormatInt(queryID, 10)
	queryBasePath := filepath.Join(s.volumePath, queryStrID)
	sourceDir := filepath.Join(queryBasePath, "source")
	resultDir := filepath.Join(queryBasePath, "result")

	if err := os.MkdirAll(sourceDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create source directory"})
		return
	}
	if err := os.MkdirAll(resultDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create result directory"})
		return
	}

	files := form.File["files"]
	if len(files) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No files provided"})
		return
	}

	for _, file := range files {
		destination := filepath.Join(sourceDir, file.Filename)
		if err := c.SaveUploadedFile(file, destination); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Failed to save file: %s", file.Filename)})
			return
		}
	}

	resp, err := s.mlClient.Detect(c.Request.Context(), queryID, queryBasePath, payload.Targets)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "ML Service failure", "details": err.Error()})
		return
	}

	if !resp.Success {
		c.JSON(http.StatusUnprocessableEntity, gin.H{"error": "Detection failed", "message": resp.ErrorMessage})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"query_id":      resp.QueryId,
		"status":        "Success",
		"instance_info": resp.InstanceInfo,
		"total":         resp.TotalObjects,
		"result_dir":    fmt.Sprintf("/results/%s/result/", queryStrID),
	})
}

func (s *HTTPService) History(c *gin.Context) {
	userID := c.GetString("user_id")

	var req models.HistoryAnswer
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid payload"})
		return
	}

	queries, err := s.dbClient.GetHistoryAnswers(c.Request.Context(), req.Quantity, userID, req.Flag)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user queries"})
		return
	}
	var response []models.HistoryResponse
	for _, queryID := range queries {
		reportPath := filepath.Join(s.volumePath, strconv.FormatInt(int64(queryID), 10), "result", "report.txt")
		if _, err := os.Stat(reportPath); os.IsNotExist(err) {
			reportPath = filepath.Join(s.volumePath, strconv.FormatInt(int64(queryID), 10), "result", "detection_summary.txt")
		}

		entries, err := ParseReport(reportPath)
		if err != nil {
			c.JSON(http.StatusNotFound, gin.H{"error": "Report not found or invalid format", "details": err.Error()})
			return
		}
		response = append(response, models.HistoryResponse{
			QueryId: queryID,
			Entries: entries,
		})
	}
	c.JSON(http.StatusOK, gin.H{
		"queries": response,
	})
}

func (s *HTTPService) AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		tokenString := c.GetHeader("Authorization")
		if tokenString == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		if len(tokenString) > 7 && tokenString[:7] == "Bearer " {
			tokenString = tokenString[7:]
		}

		token, err := jwt.Parse(tokenString, func(t *jwt.Token) (interface{}, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method")
			}
			return s.jwtSecret, nil
		})

		if err != nil || !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid claims map"})
			c.Abort()
			return
		}

		c.Set("user_id", claims["user_id"])
		c.Next()
	}
}

func ParseReport(filePath string) ([]models.ReportEntry, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open report file: %w", err)
	}
	defer file.Close()

	var entries []models.ReportEntry
	scanner := bufio.NewScanner(file)

	var currentFilename string
	step := 0

	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		if line == "---" {
			step = 0
			continue
		}

		if step == 0 {
			currentFilename = line
			step = 1
		} else if step == 1 {
			var detections []models.Detection
			if err := json.Unmarshal([]byte(line), &detections); err != nil {
				return nil, fmt.Errorf("failed to parse JSON for file %s: %w", currentFilename, err)
			}

			entries = append(entries, models.ReportEntry{
				Filename:   currentFilename,
				Detections: detections,
			})

			step = 2
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("error reading report file: %w", err)
	}

	return entries, nil
}

### .\Backend\manager\internal\services\http.go END ###

### .\Backend\test\e2e.go BEGIN ###
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

const baseURL = "http://localhost:8080/api/v1"

func main() {
	fmt.Println("=== Starting E2E Backend Test ===")

	if !waitForServer(3 * time.Second) {
		fmt.Println("[X] Aborting test due to server unavailability.")
		return
	}
	timestamp := time.Now().Unix()
	username := fmt.Sprintf("testuser_%d", timestamp)
	password := "securepassword123"

	fmt.Printf("\n[*] Registering user: %s\n", username)
	register(username, password)

	fmt.Println("\n[*] Logging in...")
	token := login(username, password)
	if token == "" {
		fmt.Println("[X] Aborting test due to login failure.")
		return
	}
	fmt.Printf("    -> Received JWT Token: %s...\n", token[:20])

	fmt.Println("\n[*] Fetching history...")
	history(token)

	fmt.Println("\n[*] Sending real files to /detect endpoint...")
	detect(token)

	fmt.Println("\n=== E2E Test Finished ===")
}

func waitForServer(timeout time.Duration) bool {
	client := http.Client{Timeout: timeout}
	for i := 0; i < 6; i++ {
		resp, err := client.Get("http://localhost:8080/health")
		if err == nil && resp.StatusCode == http.StatusOK {
			return true
		}
		fmt.Printf("[!] Waiting for server... (%d/6)\n", i+1)
		time.Sleep(5 * time.Second)
	}
	return false
}

func register(username, password string) {
	payload := map[string]string{
		"login":    username,
		"password": password,
	}
	body, _ := json.Marshal(payload)

	resp, err := http.Post(baseURL+"/auth/register", "application/json", bytes.NewBuffer(body))
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode == http.StatusCreated {
		fmt.Println("    -> Success: User registered (201 Created)")
	} else {
		bodyBytes, _ := io.ReadAll(resp.Body)
		fmt.Printf("    [X] Failed with status %d: %s\n", resp.StatusCode, string(bodyBytes))
	}
}

func login(username, password string) string {
	payload := map[string]string{
		"login":    username,
		"password": password,
	}
	body, _ := json.Marshal(payload)

	resp, err := http.Post(baseURL+"/auth/login", "application/json", bytes.NewBuffer(body))
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return ""
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		fmt.Printf("    [X] Failed with status %d: %s\n", resp.StatusCode, string(bodyBytes))
		return ""
	}

	var result map[string]string
	json.NewDecoder(resp.Body).Decode(&result)
	return result["token"]
}

func history(token string) {
	payload := map[string]any{
		"quantity": 10,
		"flag":     "test",
	}
	body, _ := json.Marshal(payload)

	req, _ := http.NewRequest(http.MethodPost, baseURL+"/history", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)
	if resp.StatusCode == http.StatusOK {
		fmt.Printf("    -> Success: History retrieved: %s\n", string(bodyBytes))
	} else {
		fmt.Printf("    [X] Failed with status %d: %s\n", resp.StatusCode, string(bodyBytes))
	}
}

func detect(token string) {
	filesToUpload := []string{
		`C:\Users\komar\OneDrive\Рабочий стол\projectM\mainRep\Backend\test\testdata\test1.jpg`,
		`C:\Users\komar\OneDrive\Рабочий стол\projectM\mainRep\Backend\test\testdata\test2.jpg`,
	}

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)

	jsonPayload := `{"targets":["person","car","apple"]}`
	if err := writer.WriteField("payload", jsonPayload); err != nil {
		fmt.Printf("    [X] Failed to write payload field: %v\n", err)
		return
	}

	filesAttached := 0
	for _, filePath := range filesToUpload {
		file, err := os.Open(filePath)
		if err != nil {
			fmt.Printf("    [X] Failed to open file %s: %v\n", filePath, err)
			continue
		}

		part, err := writer.CreateFormFile("files", filepath.Base(filePath))
		if err != nil {
			file.Close()
			fmt.Printf("    [X] Failed to create form file for %s: %v\n", filePath, err)
			continue
		}

		if _, err := io.Copy(part, file); err != nil {
			file.Close()
			fmt.Printf("    [X] Failed to copy file content for %s: %v\n", filePath, err)
			continue
		}

		file.Close()
		filesAttached++
		fmt.Printf("    -> Attached file: %s\n", filePath)
	}

	if filesAttached == 0 {
		fmt.Println("    [X] Aborting detect request: No files were successfully attached.")
		return
	}

	if err := writer.Close(); err != nil {
		fmt.Printf("    [X] Failed to close multipart writer: %v\n", err)
		return
	}

	req, err := http.NewRequest(http.MethodPost, baseURL+"/detect", body)
	if err != nil {
		fmt.Printf("    [X] Failed to create request: %v\n", err)
		return
	}

	req.Header.Set("Content-Type", writer.FormDataContentType())
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("    [X] Request failed: %v\n", err)
		return
	}
	defer resp.Body.Close()

	bodyBytes, _ := io.ReadAll(resp.Body)

	if resp.StatusCode == http.StatusInternalServerError {
		fmt.Printf("    -> Received 500 Internal Server Error.\n")
		fmt.Printf("    -> Response: %s\n", string(bodyBytes))
	} else if resp.StatusCode == http.StatusOK {
		fmt.Printf("    -> Success! ML Service responded: %s\n", string(bodyBytes))
	} else {
		fmt.Printf("    [X] Unexpected status %d: %s\n", resp.StatusCode, string(bodyBytes))
	}
}

### .\Backend\test\e2e.go END ###

### .\Backend\test\go.mod BEGIN ###
module test

go 1.24.2

### .\Backend\test\go.mod END ###

### .\docker-compose.yaml BEGIN ###
services:
  # ── ML (gRPC-сервер детекции) ────────────────────────────────
  ml:
    build:
      context: ./ML
      dockerfile: Dockerfile
    container_name: ml
    ports:
      - "50051:50051"
    volumes:
      - shared-volume:/app/volume
    networks:
      - peeky-net
    healthcheck:
      test: ["CMD-SHELL", "python -c \"import grpc; ch=grpc.insecure_channel('localhost:50051'); grpc.channel_ready_future(ch).result(timeout=5)\""]
      interval: 10s
      timeout: 10s
      retries: 5
      start_period: 30s
    restart: unless-stopped

  # ── PostgreSQL ───────────────────────────────────────────────
  db:
    image: postgres:16-alpine
    container_name: db
    environment:
      POSTGRES_USER: babkivkedah
      POSTGRES_PASSWORD: tapki.com
      POSTGRES_DB: projectml
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - peeky-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U babkivkedah -d projectml"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ── Database service (gRPC) ──────────────────────────────────
  db_service:
    build:
      context: ./Backend/database
      dockerfile: Dockerfile
    container_name: db_service
    ports:
      - "2021:2021"
    networks:
      - peeky-net
    depends_on:
      ml:
        condition: service_healthy
      db:
        condition: service_healthy
    restart: unless-stopped

  # ── Manager (HTTP API) ──────────────────────────────────────
  manager:
    build:
      context: ./Backend/manager
      dockerfile: Dockerfile
    container_name: manager
    ports:
      - "8080:8080"
    volumes:
      - shared-volume:/app/volume
    networks:
      - peeky-net
    depends_on:
      ml:
        condition: service_healthy
      db_service:
        condition: service_started
    restart: unless-stopped

volumes:
  pgdata:
  shared-volume:

networks:
  peeky-net:
    driver: bridge

### .\docker-compose.yaml END ###

### .\ML\app\core\coco_classes.py BEGIN ###
# app/core/coco_classes.py

COCO_CLASSES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    4: "airplane",
    5: "bus",
    6: "train",
    7: "truck",
    8: "boat",
    9: "traffic light",
    10: "fire hydrant",
    11: "stop sign",
    12: "parking meter",
    13: "bench",
    14: "bird",
    15: "cat",
    16: "dog",
    17: "horse",
    18: "sheep",
    19: "cow",
    20: "elephant",
    21: "bear",
    22: "zebra",
    23: "giraffe",
    24: "backpack",
    25: "umbrella",
    26: "handbag",
    27: "tie",
    28: "suitcase",
    29: "frisbee",
    30: "skis",
    31: "snowboard",
    32: "sports ball",
    33: "kite",
    34: "baseball bat",
    35: "baseball glove",
    36: "skateboard",
    37: "surfboard",
    38: "tennis racket",
    39: "bottle",
    40: "wine glass",
    41: "cup",
    42: "fork",
    43: "knife",
    44: "spoon",
    45: "bowl",
    46: "banana",
    47: "apple",
    48: "sandwich",
    49: "orange",
    50: "broccoli",
    51: "carrot",
    52: "hot dog",
    53: "pizza",
    54: "donut",
    55: "cake",
    56: "chair",
    57: "couch",
    58: "potted plant",
    59: "bed",
    60: "dining table",
    61: "toilet",
    62: "tv",
    63: "laptop",
    64: "mouse",
    65: "remote",
    66: "keyboard",
    67: "cell phone",
    68: "microwave",
    69: "oven",
    70: "toaster",
    71: "sink",
    72: "refrigerator",
    73: "book",
    74: "clock",
    75: "vase",
    76: "scissors",
    77: "teddy bear",
    78: "hair drier",
    79: "toothbrush"
}

# Обратный словарь: имя → ID
COCO_CLASS_NAMES_TO_IDS = {name: id for id, name in COCO_CLASSES.items()}
### .\ML\app\core\coco_classes.py END ###

### .\ML\app\core\di_container.py BEGIN ###
# app/services/container.py
from app.services.model_loader import ModelLoader

class ServiceContainer:
    """Простой контейнер зависимостей"""

    def __init__(self):
        self._file_manager = None
        self._model_loader = None

    @property
    def model_loader(self):
        if self._model_loader is None:
            self._model_loader = ModelLoader(
                model_filename="yolov8n.pt",
                device="cpu"  # или "cuda", если есть GPU
            )
        return self._model_loader
### .\ML\app\core\di_container.py END ###

### .\ML\app\grps\protos\detector.proto BEGIN ###
syntax = "proto3";
package grps;
option go_package = "sirius.ml.v1;ml1";

service Detector {
  rpc ImageDetection (DetectionRequest) returns (DetectionResponse);
}

message DetectionRequest {
  int64 query_id = 1;
  string dir_path = 2;
  repeated string targets = 3;
}

message DetectionResponse {
  int64 query_id = 1;
  string result_path = 2;
  bool success = 3;
  repeated InstanceInfo instance_info = 4; // [{"person": 3}, {"car": 2}]
  string error_message = 5;
  int32 total_objects = 6;
}

message InstanceInfo {
  string class_name = 1;
  float confidience = 2;
  // Bounding box: [x_min, y_min, x_max, y_max]
  repeated float bbox = 3;
}


### .\ML\app\grps\protos\detector.proto END ###

### .\ML\app\grps\protos\detector_pb2.py BEGIN ###
# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: detector.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x64\x65tector.proto\x12\x04grps\"G\n\x10\x44\x65tectionRequest\x12\x10\n\x08query_id\x18\x01 \x01(\x03\x12\x10\n\x08\x64ir_path\x18\x02 \x01(\t\x12\x0f\n\x07targets\x18\x03 \x03(\t\"\xa4\x01\n\x11\x44\x65tectionResponse\x12\x10\n\x08query_id\x18\x01 \x01(\x03\x12\x13\n\x0bresult_path\x18\x02 \x01(\t\x12\x0f\n\x07success\x18\x03 \x01(\x08\x12)\n\rinstance_info\x18\x04 \x03(\x0b\x32\x12.grps.InstanceInfo\x12\x15\n\rerror_message\x18\x05 \x01(\t\x12\x15\n\rtotal_objects\x18\x06 \x01(\x05\"E\n\x0cInstanceInfo\x12\x12\n\nclass_name\x18\x01 \x01(\t\x12\x13\n\x0b\x63onfidience\x18\x02 \x01(\x02\x12\x0c\n\x04\x62\x62ox\x18\x03 \x03(\x02\x32M\n\x08\x44\x65tector\x12\x41\n\x0eImageDetection\x12\x16.grps.DetectionRequest\x1a\x17.grps.DetectionResponseB\x12Z\x10sirius.ml.v1;ml1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'detector_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  _globals['DESCRIPTOR']._options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\020sirius.ml.v1;ml1'
  _globals['_DETECTIONREQUEST']._serialized_start=24
  _globals['_DETECTIONREQUEST']._serialized_end=95
  _globals['_DETECTIONRESPONSE']._serialized_start=98
  _globals['_DETECTIONRESPONSE']._serialized_end=262
  _globals['_INSTANCEINFO']._serialized_start=264
  _globals['_INSTANCEINFO']._serialized_end=333
  _globals['_DETECTOR']._serialized_start=335
  _globals['_DETECTOR']._serialized_end=412
# @@protoc_insertion_point(module_scope)

### .\ML\app\grps\protos\detector_pb2.py END ###

### .\ML\app\grps\protos\detector_pb2_grpc.py BEGIN ###
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from . import detector_pb2 as detector__pb2


class DetectorStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ImageDetection = channel.unary_unary(
                '/grps.Detector/ImageDetection',
                request_serializer=detector__pb2.DetectionRequest.SerializeToString,
                response_deserializer=detector__pb2.DetectionResponse.FromString,
                )


class DetectorServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ImageDetection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_DetectorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ImageDetection': grpc.unary_unary_rpc_method_handler(
                    servicer.ImageDetection,
                    request_deserializer=detector__pb2.DetectionRequest.FromString,
                    response_serializer=detector__pb2.DetectionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grps.Detector', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Detector(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ImageDetection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grps.Detector/ImageDetection',
            detector__pb2.DetectionRequest.SerializeToString,
            detector__pb2.DetectionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

### .\ML\app\grps\protos\detector_pb2_grpc.py END ###

### .\ML\app\grps\protos\__init__.py BEGIN ###

### .\ML\app\grps\protos\__init__.py END ###

### .\ML\app\grps\server.py BEGIN ###
# app/grps/server.py
import logging
from concurrent import futures
import grpc
from app.scenaries.detect_image import ImageDetectionUseCase

# Импортируем сгенерированные protobuf-модули
from app.grps.protos import detector_pb2, detector_pb2_grpc

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DetectorService(detector_pb2_grpc.DetectorServicer):
    """Реализация сервиса Detector из обновлённого detector.proto"""

    def __init__(self):
        logger.info("DetectorService initialized")
        self.image_detection_usecase = ImageDetectionUseCase()
    def ImageDetection(self, request: detector_pb2.DetectionRequest, context) -> detector_pb2.DetectionResponse:
        """
        Новая реализация метода:
        - Принимает query_id, dir_path, targets
        - Запускает детекцию по директории (или файлу)
        - Возвращает result_path, query_id, статистику и статус
        """
        query_id = int(request.query_id)
        dir_path = request.dir_path
        targets = list(request.targets) 

        logger.info(f"[Query {query_id}] Received detection request: dir_path={dir_path}, targets={targets}")

        try:
            save_path, counts, instance_infos = self.image_detection_usecase.execute(
                query_id=query_id,
                dir_path=dir_path,
                targets=targets,
                min_confidence=0.5,
            )

            # === Формирование списка InstanceInfo ===
            grpc_instances = []
            for info in instance_infos:
                grpc_instances.append(
                    detector_pb2.InstanceInfo(
                        class_name=str(info.get("class_name", "")),
                        confidience=float(info.get("confidence", "")),
                        bbox=list(map(float, info.get("bbox", []))),
                    )
                )

            # Общее количество объектов
            total_objects = int(sum(counts.values())) if counts else len(instance_infos)

            logger.info(f"[Query {query_id}] Detection successful. Found {total_objects} objects. Results saved to {save_path}")

            return detector_pb2.DetectionResponse(query_id=query_id,
                                                  result_path=save_path,
                                                  success=True,
                                                  instance_info=grpc_instances,
                                                  total_objects=total_objects)

        except Exception as e:
            logger.exception(f"[Query {query_id}] Error during detection")
            return self._error_response(query_id, f"Detection failed: {str(e)}")

    @staticmethod
    def _error_response(query_id: int, message: str) -> detector_pb2.DetectionResponse:
        """Вспомогательный метод для формирования ошибки с query_id"""
        logger.error(f"[Query {query_id}] Returning error: {message}")
        return detector_pb2.DetectionResponse(
            query_id=query_id,
            result_path="",
            success=False,
            error_message=message,
            total_objects=0
        )

def serve(port: int = 50051) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    detector_pb2_grpc.add_DetectorServicer_to_server(DetectorService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f"Detector gRPC server started on port {port}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
### .\ML\app\grps\server.py END ###

### .\ML\app\grps\__init__.py BEGIN ###

### .\ML\app\grps\__init__.py END ###

### .\ML\app\scenaries\detect_batch_image.py BEGIN ###

### .\ML\app\scenaries\detect_batch_image.py END ###

### .\ML\app\scenaries\detect_image.py BEGIN ###
from ultralytics import YOLO
from pathlib import Path
from app.utils.generate_report import save_summary_report_v2
from pathlib import Path
from typing import List
from app.utils.names_to_ids import class_names_to_ids
from app.core.di_container import ServiceContainer

class ImageDetectionUseCase:
    def __init__(self):
        container = ServiceContainer()
        self.model_loader = container.model_loader

    def execute(
        self,
        query_id: int,
        dir_path: str,
        targets: List[str],
        min_confidence: float = 0.5
    ) -> tuple[str, dict, list[dict]]:
        # Валидация
        if not dir_path:
            raise ValueError("dir_path cannot be empty")
        if not Path(dir_path).exists():
            raise FileNotFoundError(f"Path does not exist: {dir_path}")

        # Подготовка путей
        base = Path(dir_path)
        source_path = str(base / "detect" / f"query_{query_id}" / "source")
        save_path = str(base / "detect" / f"query_{query_id}" / "result")

        # Загрузка модели и преобразование целей
        model = self.model_loader.get_model()
        target_ids = class_names_to_ids(targets) if targets else None

        # Запуск детекции
        counts, instance_infos = self._detect_image(
            source_path=source_path,
            save_path=save_path,
            target_ids=target_ids,
            min_confidence=min_confidence,
            model=model
        )
        return save_path, counts, instance_infos
           

    def _detect_image(self, source_path: str, save_path: str, target_ids=None, min_confidence=0.5, model: YOLO = None):
        """
        Выполняет детекцию на одном изображении,
        а также сохраняет результат в папку results
        """
        results = model(
            source_path,
            conf=min_confidence,
            classes=target_ids,      # ← фильтрация на уровне модели
            save=True,
            project=Path(save_path).parent, 
            name=Path(save_path).name, 
            exist_ok=True,
            verbose=False,
        )
        
        if results:
            print(f"💾 Файл сохранён в: {results[0].save_dir}")
            print(f"📦 Найдено боксов: {len(results[0].boxes)}")
        else:
            print("⚠️ Нет результатов")

        # Собираем результаты — считаем по классам и собираем подробности по каждому боксу
        counts: dict[str, int] = {}
        names = model.names
        instance_infos: list[dict] = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                cls_name = names[cls_id]

                # Счётчик по классам
                counts[cls_name] = counts.get(cls_name, 0) + 1

                # Детальная информация по конкретному боксу
                confidence = float(box.conf.item()) if hasattr(box, "conf") else None
                bbox = box.xyxy[0].tolist() if hasattr(box, "xyxy") else None

                instance_infos.append(
                    {
                        "class_name": cls_name,
                        "count": 1,
                        "confidence": confidence,
                        "bbox": [float(v) for v in bbox] if bbox is not None else [],
                    }
                )
        if results:
            report_file = Path(save_path) / "report.txt"
            save_summary_report_v2(results, model.names, str(report_file))
        else:
            print("⚠️ Нет обработанных изображений — отчёт не создан")

        return counts, instance_infos

### .\ML\app\scenaries\detect_image.py END ###

### .\ML\app\scenaries\detect_video.py BEGIN ###

### .\ML\app\scenaries\detect_video.py END ###

### .\ML\app\scripts\download_model.py BEGIN ###
import requests
from pathlib import Path
from tqdm import tqdm

def download_model():
    # Путь к папке models
    PROJECT_ROOT = Path(__file__).parent.parent  # Projects/ImageClassifer
    MODEL_DIR = PROJECT_ROOT / "models"
    MODEL_DIR.mkdir(exist_ok=True, parents=True)
    
    # Путь куда сохранить модель
    model_path = MODEL_DIR / "yolov8n.pt"
    
    # Если модель уже есть - пропускаем
    if model_path.exists():
        print(f"✅ Модель уже существует: {model_path}")
        return str(model_path)
    
    # URL для скачивания YOLOv8n
    url = "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt"
    
    print(f"Скачиваю модель в: {model_path}")
    
    # Скачиваем с прогресс-баром
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    # Получаем размер файла
    total_size = int(response.headers.get('content-length', 0))
    
    # Сохраняем файл
    with open(model_path, 'wb') as f, tqdm(
        desc=model_path.name,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))
    
    print(f"✅ Модель скачана: {model_path}")
    return str(model_path)

# Использование
if __name__ == "__main__":
    model_file = download_model()
    
    # Теперь загружаем модель через YOLO
    from ultralytics import YOLO
    model = YOLO(model_file)
    print("Модель готова к использованию!")
### .\ML\app\scripts\download_model.py END ###

### .\ML\app\scripts\start_upload_container.bat BEGIN ###
@echo off
powershell -ExecutionPolicy Bypass -File "upload_container_images.ps1"
pause
### .\ML\app\scripts\start_upload_container.bat END ###

### .\ML\app\scripts\upload_container_images.ps1 BEGIN ###
# copy_volume.ps1
# Exports /app/volume content from container 'ml' to local folder 'cont_volume'

param(
    [string]$ContainerName = "ml",
    [string]$ContainerPath = "/app/volume",
    [string]$LocalDest = "./cont_volume",
    [switch]$WithTimestamp,
    [switch]$OpenAfter
)

# Generate destination folder name
if ($WithTimestamp) {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $destinationFolder = "${LocalDest}_${timestamp}"
} else {
    $destinationFolder = $LocalDest
}

Write-Host "Docker Volume Export" -ForegroundColor Cyan
Write-Host "Container: $ContainerName" -ForegroundColor Gray
Write-Host "Source: ${ContainerPath}/." -ForegroundColor Gray
Write-Host "Destination: $destinationFolder" -ForegroundColor Yellow
Write-Host ""

# Check if container is running
$containerStatus = docker ps --filter "name=^${ContainerName}$" --format "{{.Status}}" -a
if (-not $containerStatus) {
    Write-Host "ERROR: Container '$ContainerName' not found!" -ForegroundColor Red
    Write-Host "Available containers:" -ForegroundColor DarkGray
    docker ps -a --format "table {{.Names}}\t{{.Status}}"
    exit 1
}

# Create destination folder
New-Item -ItemType Directory -Force -Path $destinationFolder -ErrorAction SilentlyContinue | Out-Null

# Copy contents (note the /. at end - copies content, not the folder itself)
Write-Host "Copying files..." -ForegroundColor Gray
docker cp "${ContainerName}:${ContainerPath}/." $destinationFolder

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Copy failed!" -ForegroundColor Red
    exit 1
}

# Wait for I/O to complete
Start-Sleep -Milliseconds 500

# === Statistics ===
$allItems = Get-ChildItem -Path $destinationFolder -Force -ErrorAction SilentlyContinue
$files = $allItems | Where-Object { !$_.PSIsContainer }
$folders = $allItems | Where-Object { $_.PSIsContainer }

Write-Host ""
Write-Host "Copy completed!" -ForegroundColor Green
Write-Host "Path: $(Resolve-Path $destinationFolder)" -ForegroundColor Yellow
Write-Host "Total items: $($allItems.Count)" -ForegroundColor Green
Write-Host "Files: $($files.Count)" -ForegroundColor Green
Write-Host "Folders: $($folders.Count)" -ForegroundColor Green

# File details (top 10)
if ($files.Count -gt 0) {
    Write-Host ""
    Write-Host "Files (first 10):" -ForegroundColor DarkGray
    $files | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object {
        $size = if ($_.Length -gt 1GB) { "$([Math]::Round($_.Length/1GB, 2)) GB" }
                elseif ($_.Length -gt 1MB) { "$([Math]::Round($_.Length/1MB, 2)) MB" }
                elseif ($_.Length -gt 1KB) { "$([Math]::Round($_.Length/1KB, 2)) KB" }
                else { "$($_.Length) B" }
        Write-Host "   - $($_.Name) ($size)" -ForegroundColor DarkGray
    }
    if ($files.Count -gt 10) {
        Write-Host "   ... and $($files.Count - 10) more files" -ForegroundColor DarkGray
    }
}

# Folder details
if ($folders.Count -gt 0) {
    Write-Host ""
    Write-Host "Subfolders:" -ForegroundColor DarkGray
    $folders | ForEach-Object {
        $count = (Get-ChildItem -Path $_.FullName -Recurse -File -ErrorAction SilentlyContinue).Count
        Write-Host "   - $($_.Name) ($count files inside)" -ForegroundColor DarkCyan
    }
}

# Open folder in Explorer
if ($OpenAfter) {
    Write-Host ""
    Write-Host "Opening folder..." -ForegroundColor Cyan
    Start-Sleep -Milliseconds 300
    Invoke-Item (Resolve-Path $destinationFolder)
}
### .\ML\app\scripts\upload_container_images.ps1 END ###

### .\ML\app\services\model_loader.py BEGIN ###

from ultralytics import YOLO
from pathlib import Path

__all__ = ['ModelLoader', 'public_function']

class ModelLoader:
    def __init__(self, model_filename="yolov8n.pt", device="cpu"):
        self.model_filename = model_filename
        self.device = device
        self.model = None
        self.models_dir = self.__get_models_dir()

    def __get_models_dir(self) -> str:
        """Определяет папку с моделями"""
        current_dir = Path(__file__).parent.parent
        models_dir = current_dir / "models"
        
        if not models_dir.exists():
            models_dir = Path.cwd() / "models"
            models_dir.mkdir(exist_ok=True)
        
        return models_dir
    
    def __load_model(self) -> bool:
        """Загрузка модели из папки models"""
        try:
            model_path = self.models_dir / self.model_filename

            if not model_path.exists():
                raise FileNotFoundError(
                    f"Модель '{self.model_filename}' не найдена в папке {self.models_dir}\n"
                    f"Убедитесь, что файл модели находится в папке 'models'"
                )
            
            self.model = YOLO(model_path)
            
            self.model.to(self.device)
            
            return True
            
        except FileNotFoundError as e:
            raise
        except Exception as e:
            raise

    def get_model(self) -> YOLO:
        if self.model is None:
            try:
                self.__load_model()
            except:
                raise RuntimeError(f"Ошибка во время загрузки {self.model_filename} в {self.device}")
        return self.model
         

        

    

### .\ML\app\services\model_loader.py END ###

### .\ML\app\services\__init__.py BEGIN ###

### .\ML\app\services\__init__.py END ###

### .\ML\app\utils\generate_report.py BEGIN ###
from ultralytics.engine.results import Results
import json
from pathlib import Path


def save_summary_report(
    results: list[Results],
    model_names: dict,
    output_txt_path: str
) -> None:
    """
    Сохраняет сводный TXT-отчёт по всем обработанным изображениям.

    Формат отчёта:
        image1.jpg
        {"person": 2, "car": 1}
        ---
        image2.jpg
        {"dog": 1}
        ---
        ...

    Args:
        results (list[Results]): Список результатов от YOLO-модели (результат вызова model(...))
        model_names (dict): Словарь {class_id: "class_name"}, обычно model.names
        output_txt_path (str): Путь к итоговому .txt файлу (например, "results/detect/query_123/summary.txt")
    """
    output_path = Path(output_txt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            # Получаем путь к исходному изображению
            img_path = getattr(result, 'path', 'unknown_image.jpg')
            img_name = Path(img_path).name

            # Считаем объекты по классам
            counts = {}
            if hasattr(result, 'boxes') and result.boxes is not None:
                for cls_id in result.boxes.cls.cpu().numpy():
                    cls_name = model_names[int(cls_id)]
                    counts[cls_name] = counts.get(cls_name, 0) + 1

            # Записываем в файл
            f.write(f"{img_name}\n")
            f.write(json.dumps(counts, ensure_ascii=False, indent=0))
            f.write("\n---\n")

    print(f"📄 Сводный отчёт сохранён: {output_path}")


def save_summary_report_v2(
    results: list[Results],
    model_names: dict,
    output_txt_path: str
) -> None:
    """
    Расширенный TXT-отчёт: отдельная запись для каждой найденной сущности
    с указанием класса, уверенности и координат bounding box.

    Формат отчёта:
        image1.jpg
        [
          {"class": "person", "confidence": 0.92, "bbox": [x1, y1, x2, y2]},
          {"class": "car", "confidence": 0.81, "bbox": [x1, y1, x2, y2]}
        ]
        ---
        image2.jpg
        []
        ---
    """
    output_path = Path(output_txt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            img_path = getattr(result, 'path', 'unknown_image.jpg')
            img_name = Path(img_path).name

            detections: list[dict] = []

            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes

                cls_ids = boxes.cls.cpu().tolist() if hasattr(boxes, "cls") else []
                confs = boxes.conf.cpu().tolist() if hasattr(boxes, "conf") else []
                xyxy = boxes.xyxy.cpu().tolist() if hasattr(boxes, "xyxy") else []

                for idx, cls_id in enumerate(cls_ids):
                    record: dict = {
                        "class": model_names.get(int(cls_id), str(int(cls_id))),
                    }

                    if idx < len(confs):
                        record["confidence"] = float(confs[idx])

                    if idx < len(xyxy):
                        # x1, y1, x2, y2
                        record["bbox"] = [float(v) for v in xyxy[idx]]

                    detections.append(record)

            f.write(f"{img_name}\n")
            f.write(json.dumps(detections, ensure_ascii=False))
            f.write("\n---\n")

    print(f"📄 Детализированный отчёт (v2) сохранён: {output_path}")
### .\ML\app\utils\generate_report.py END ###

### .\ML\app\utils\names_to_ids.py BEGIN ###
from app.core.coco_classes import COCO_CLASS_NAMES_TO_IDS
def class_names_to_ids(target_classes):
    """Преобразует список имён классов в ID из COCO."""
    if not target_classes:
        return None
    class_ids = []
    for cls_name in target_classes:
        if cls_name in COCO_CLASS_NAMES_TO_IDS:
            class_ids.append(COCO_CLASS_NAMES_TO_IDS[cls_name])
        # Игнорируем неизвестные классы (можно изменить на ошибку)
    return class_ids if class_ids else None
### .\ML\app\utils\names_to_ids.py END ###

### .\ML\app\utils\__init__.py BEGIN ###

### .\ML\app\utils\__init__.py END ###

### .\ML\dockerfile BEGIN ###
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libglib2.0-0 libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    && rm -rf /root/.cache/pip

# Просто копируем весь код (включая уже сгенерированные _pb2.py файлы)
COPY . .

EXPOSE 50051
CMD ["python", "main.py"]
### .\ML\dockerfile END ###

### .\ML\main.py BEGIN ###
# main.py
import subprocess
import sys
import os
from pathlib import Path


def main():
    print("🚀 Запускаю gRPC сервер...🚀🚀🚀🚀")
    
    if not os.path.exists("app/grps/server.py"):
        print("❌ Файл server.py не найден")
        return

    try:
        # Запускаем как модуль И захватываем вывод
        result = subprocess.run(
            [sys.executable, "-m", "app.grps.server"],
            capture_output=False,  # Выводим всё в консоль напрямую
            text=True,
            check=False  # Не выбрасываем исключение автоматически
        )
        
        if result.returncode != 0:
            print(f"\n⚠️ Сервер завершился с кодом: {result.returncode}")
        else:
            print("\n✅ Сервер остановлен штатно")
            
    except KeyboardInterrupt:
        print("\n🛑 Принудительная остановка")
    except Exception as e:
        print(f"💥 Аварийная ошибка: {e}")

if __name__ == "__main__":
    main()
### .\ML\main.py END ###

### .\ML\README.md BEGIN ###
\#Main.py

Перед тем как запускать main.py нужно:



1. python -m pip install --upgrade pip - обновит установщик пакетов pip



2\. pip install -r requirements.txt - установит библиотеки для работы приложения



3\. Запустить из файла main.py приложение



После этих действий запустится fastapi swagger, поидее, по ссылке http://localhost:8000/docs, можно будет перейти к нему







\#DOCKER

Установить Docker desktop



Запустить Docker desktop, убедиться что движок запущен



docker build --no-cache -t ml\_service . - Сбилдить образ контейнера



docker run -p 8000:8000 --name ml\_service\_container ml\_service - развернуть контейнер из образа



\#О скриптах



Есть 2 скрипта



1. download\_model.py - Находится в app/scripts/, загружает модель YOLO8, просто типо на комп грузит модельку. чтобы она локально у тебя была

2\. upload\_container\_images.ps1 - Этот скрипт нужен для того, чтобы выгружать из контейнера docker, результаты, типо изображения с баундин боксами. Он используется только при запущенном контейнере. Просто вытягивает результаты, создавая в проекте папку results\_container.



ВАЖНО Запускается при помощи другого файла: start\_upload\_container.bat


### .\ML\README.md END ###

### .\ML\requirements.txt BEGIN ###
��- - e x t r a - i n d e x - u r l   h t t p s : / / d o w n l o a d . p y t o r c h . o r g / w h l / c p u 
 
 
 
 #   = = =    "'+  !!"  ( ?>@O4>:  2065=! )   = = = 
 
 p r o t o b u f = = 4 . 2 5 . 3 
 
 g r p c i o = = 1 . 6 2 . 0 
 
 g r p c i o - t o o l s = = 1 . 6 2 . 0 
 
 
 
 #   = = =   P y T o r c h   C P U   ( O2=>,   GB>1K  =5  A:0G0;AO  C U D A )   = = = 
 
 t o r c h = = 2 . 4 . 0 + c p u 
 
 t o r c h v i s i o n = = 0 . 1 9 . 0 + c p u 
 
 t o r c h a u d i o = = 2 . 4 . 0 + c p u 
 
 
 
 #   = = =   AB0;L=K5  7028A8<>AB8  = = = 
 
 a n n o t a t e d - d o c = = 0 . 0 . 3 
 
 a n n o t a t e d - t y p e s = = 0 . 7 . 0 
 
 a n y i o = = 4 . 1 1 . 0 
 
 c e r t i f i = = 2 0 2 5 . 1 0 . 5 
 
 c h a r s e t - n o r m a l i z e r = = 3 . 4 . 4 
 
 c l i c k = = 8 . 3 . 0 
 
 c o l o r a m a = = 0 . 4 . 6 
 
 f a s t a p i = = 0 . 1 2 0 . 4 
 
 f i l e l o c k = = 3 . 2 0 . 0 
 
 f s s p e c = = 2 0 2 5 . 1 0 . 0 
 
 g u n i c o r n = = 2 3 . 0 . 0 
 
 h 1 1 = = 0 . 1 6 . 0 
 
 h u g g i n g f a c e - h u b = = 0 . 3 6 . 0 
 
 i d n a = = 3 . 1 1 
 
 J i n j a 2 = = 3 . 1 . 6 
 
 M a r k u p S a f e = = 3 . 0 . 3 
 
 m p m a t h = = 1 . 3 . 0 
 
 n e t w o r k x = = 3 . 5 
 
 n u m p y = = 2 . 2 . 6 
 
 o p e n c v - p y t h o n - h e a d l e s s = = 4 . 1 2 . 0 . 8 8 
 
 p a c k a g i n g = = 2 5 . 0 
 
 p i l l o w = = 1 2 . 0 . 0 
 
 p y d a n t i c = = 2 . 1 2 . 3 
 
 p y d a n t i c _ c o r e = = 2 . 4 1 . 4 
 
 p y d a n t i c _ s e t t i n g s = = 2 . 1 1 . 0 
 
 p y t h o n - d o t e n v = = 1 . 2 . 1 
 
 p y t h o n - m u l t i p a r t = = 0 . 0 . 2 0 
 
 P y Y A M L = = 6 . 0 . 3 
 
 r e g e x = = 2 0 2 5 . 1 0 . 2 3 
 
 r e q u e s t s = = 2 . 3 2 . 5 
 
 s a f e t e n s o r s = = 0 . 6 . 2 
 
 s e t u p t o o l s = = 8 0 . 9 . 0 
 
 s n i f f i o = = 1 . 3 . 1 
 
 s t a r l e t t e = = 0 . 4 9 . 3 
 
 s y m p y = = 1 . 1 4 . 0 
 
 t o k e n i z e r s = = 0 . 2 2 . 1 
 
 t q d m = = 4 . 6 7 . 1 
 
 t r a n s f o r m e r s = = 4 . 5 7 . 1 
 
 t y p i n g - i n s p e c t i o n = = 0 . 4 . 2 
 
 t y p i n g _ e x t e n s i o n s = = 4 . 1 5 . 0 
 
 u r l l i b 3 = = 2 . 5 . 0 
 
 u v i c o r n = = 0 . 3 8 . 0 
 
 w h e e l = = 0 . 4 5 . 1 
 
 u l t r a l y t i c s = = 8 . 3 . 2 3 9 
### .\ML\requirements.txt END ###

### .\ML\test_client.py BEGIN ###
# app/grps/test_client.py
import grpc
from collections import defaultdict
from app.grps.protos import detector_pb2, detector_pb2_grpc


def print_detection_response(response: "detector_pb2.DetectionResponse") -> None:
    """
    Выводит все поля DetectionResponse в удобочитаемом формате
    с учётом новой схемы: instance_info + bbox.
    """
    print("=" * 50)
    print("📄 DETECTION RESPONSE DETAILS")
    print("=" * 50)
    print(f"Query ID:        {response.query_id}")
    print(f"Result Path:     {response.result_path}")
    print(f"Success:         {response.success}")

    if not response.success:
        print(f"Error Message:   {response.error_message}")
        print("=" * 50)
        return

    print(f"Total Objects:   {response.total_objects}")

    # Детальная информация по каждому найденному объекту
    print("\nInstances:")
    if response.instance_info:
        for idx, inst in enumerate(response.instance_info, start=1):
            bbox_str = (
                f"[{', '.join(f'{v:.2f}' for v in inst.bbox)}]"
                if inst.bbox
                else "[]"
            )
            print(
                f"  #{idx}: class={inst.class_name}, "
                f"confidence={inst.confidience}, "
                f"bbox={bbox_str}"
            )
    else:
        print("  (no instance_info entries)")

    print("=" * 50)
def main():
    # Подключаемся к серверу
    channel = grpc.insecure_channel('localhost:50051')
    stub = detector_pb2_grpc.DetectorStub(channel)

    # Параметры запроса
    query_id = 3
    dir_path = "volume"  # ← замените на реальный путь к папке или файлу!
    targets = []       # ← классы, которые нужно искать (оставьте [] для всех)

    # Формируем запрос
    request = detector_pb2.DetectionRequest(
        query_id=query_id,
        dir_path=dir_path,
        targets=targets
    )

    print(f"📤 Отправляю запрос:")
    print(f"   query_id: {request.query_id}")
    print(f"   dir_path: {request.dir_path}")
    print(f"   targets:  {list(request.targets)}")

    try:
        response = stub.ImageDetection(request)
        
        if response.success:
            print_detection_response(response)
        else:
            print(f"\n❌ Ошибка: {response.error_message}")
            
    except grpc.RpcError as e:
        print(f"\n❌ gRPC ошибка: {e.code().name} — {e.details()}")
    finally:
        channel.close()

if __name__ == '__main__':
    main()
### .\ML\test_client.py END ###

### .\project.md BEGIN ###
### DIRECTORY . FOLDER STRUCTURE ###
DIR Backend/
    DIR database/
        DIR cmd/
            FILE main.go
        DIR config/
            FILE config.yaml
        DIR contract/
            FILE database.pb.go
            FILE database_grpc.pb.go
        FILE Dockerfile
        FILE go.mod
        FILE go.sum
        DIR internal/
            DIR app/
                FILE app.go
                DIR grpc/
                    FILE app.go
            DIR config/
                FILE config.go
            DIR handlers/
                DIR grpc/
                    FILE server.go
            DIR migrations/
                FILE 1_init_schema.down.sql
                FILE 1_init_schema.up.sql
            DIR migrator/
                FILE migrator.go
            DIR models/
                FILE models.go
            DIR repository/
                FILE database.go
            DIR services/
                FILE database.go
    DIR manager/
        DIR cmd/
            FILE main.go
        DIR config/
            FILE config.yaml
        DIR contract/
            DIR database/
                FILE database.pb.go
                FILE database_grpc.pb.go
            DIR ml/
                FILE ml.pb.go
                FILE ml_grpc.pb.go
        FILE Dockerfile
        FILE go.mod
        FILE go.sum
        DIR internal/
            DIR app/
                FILE app.go
                DIR http/
                    FILE app.go
            DIR config/
                FILE config.go
            DIR models/
                FILE models.go
            DIR repository/
                DIR database/
                    FILE client.go
                DIR ml/
                    FILE client.go
            DIR router/
                FILE router.go
            DIR services/
                FILE http.go
            DIR volume/
    DIR test/
        FILE e2e.go
        FILE go.mod
        DIR testdata/
            FILE test1.jpg
            FILE test2.jpg
FILE docker-compose.yaml
DIR Frontend/
    DIR popki-first/
        FILE .gitignore
        FILE eslint.config.js
        FILE index.html
        FILE package-lock.json
        FILE package.json
        DIR public/
            FILE razminirovanie.png
            FILE Rectangle_10.png
            FILE Rectangle_11.png
            FILE Rectangle_12.png
            FILE Rectangle_13.png
            FILE Rectangle_15.png
        FILE README.md
        DIR src/
            FILE App.css
            FILE App.jsx
            DIR Components/
                FILE About.jsx
                FILE Button.jsx
                FILE Faqs.jsx
                FILE Greeting.jsx
                FILE Header.jsx
                FILE Rights.jsx
                FILE TryPeeky.jsx
                FILE Yolo.jsx
            FILE index.css
            FILE main.jsx
            DIR Pages/
                FILE Auth.jsx
                FILE GreetingsPage.jsx
                FILE Registration.jsx
        FILE vite.config.js
DIR ML/
    FILE .gitignore
    DIR app/
        DIR core/
            FILE coco_classes.py
            FILE di_container.py
        DIR grps/
            DIR protos/
                FILE detector.proto
                FILE detector_pb2.py
                FILE detector_pb2_grpc.py
                FILE __init__.py
            FILE server.py
            FILE __init__.py
        DIR scenaries/
            FILE detect_batch_image.py
            FILE detect_image.py
            FILE detect_video.py
        DIR scripts/
            FILE download_model.py
            FILE start_upload_container.bat
            FILE upload_container_images.ps1
        DIR services/
            FILE model_loader.py
            FILE __init__.py
        DIR utils/
            FILE generate_report.py
            FILE names_to_ids.py
            FILE __init__.py
    FILE dockerfile
    FILE main.py
    FILE README.md
    FILE requirements.txt
    FILE test_client.py
FILE project.md
FILE README.md
### DIRECTORY . FOLDER STRUCTURE ###

### DIRECTORY . FLATTENED CONTENT ###

### .\project.md END ###

### .\README.md BEGIN ###
��#   m a i n R e p 
 
 
### .\README.md END ###

### DIRECTORY . FLATTENED CONTENT ###
