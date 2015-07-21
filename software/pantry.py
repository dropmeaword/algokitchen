from server import http
import bottle

def main():
    http.init(wwwpath='../webapp/www', debug=True)
    bottle.run(host='localhost', port=8080)

if __name__ == '__main__':
	main()
