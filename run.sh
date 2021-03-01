
echo "Installing requirements:"
pip install -r requirements.txt
echo ""

echo "Setting up folders:"
mkdir -p /tmp/dropbox/client
mkdir -p /tmp/dropbox/server
tree /tmp/dropbox
echo ""

echo "Starting server:"
# The following enviroment variables are used to run a client & a server.
export CLIENT_CMD='python3 -c "import test_homework as th; th.client()" -- hey_client /tmp/dropbox/client /tmp/dropbox/server'
export SERVER_CMD='python3 -c "import test_homework as th; th.server()" -- hey_client /tmp/dropbox/client /tmp/dropbox/server'
echo ""
