package serve

import (
	"strconv"

	"github.com/gin-gonic/gin"
	api "github.com/phanirithvij/btp/central/server/api"
)

// Serve A function which serves the server
func Serve(port int) {
	router := gin.Default()
	api.RegisterEndPoints(router)
	router.Run(":" + strconv.Itoa(port))
}
