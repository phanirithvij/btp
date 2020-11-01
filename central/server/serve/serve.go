package serve

import (
	"strconv"

	"github.com/gin-gonic/gin"
	v1 "github.com/phanirithvij/btp/central/server/api/v1"
	v2 "github.com/phanirithvij/btp/central/server/api/v2"
)

// Serve A function which serves the server
func Serve(port int) {
	router := gin.Default()

	v1gp := router.Group("/api/v1")
	{
		v1gp.GET("/read", v1.ReadEndpoint)
	}

	v2gp := router.Group("/api/v2")
	{
		v2gp.GET("/read", v2.ReadEndpoint)
	}

	router.Run(":" + strconv.Itoa(port))
}
