import transmissionrpc
import flask
from werkzeug import secure_filename


config = {}
with open('config.ini', 'r') as file:
    for line in file.read().splitlines():
        line = line.split('==')
        config[line[0]] = line[1]

app = flask.Flask(__name__)  # Initialize our application
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # Set the upload limit to 1MiB
app.secret_key = config['SECRET_KEY']

tc = transmissionrpc.Client('localhost', port=9091, user=config['USERNAME'], password=config['PASSWORD'])


def processNewTorrent(torrentfile):
    torrentID = tc.add_torrent('file:///home/phil/snakebox/static/torrents/%s' % torrentfile)
    return torrentID

@app.route('/', methods=['GET', 'POST'])
def index():
    if flask.request.method == 'POST':
        uploaded = flask.request.files.getlist("file[]")
        for f in uploaded:
            if secure_filename(f.filename):
                f.save('static/torrents/%s' % secure_filename(f.filename))
                print 'Uploaded file "%s"' % secure_filename(f.filename)
                processNewTorrent(secure_filename(f.filename))
                flask.flash(flask.Markup('Successfully uploaded torrent %s. Download starting...') % secure_filename(
                    f.filename))
            else:
                flask.flash('Invalid filename.', flask.url_for(index))

        return flask.redirect(flask.url_for('index'))  # Upload done, refresh.
    else:
        return flask.render_template('index.html', torrents=tc.get_torrents())


if __name__ == '__main__':
    app.debug = True
    app.run(port=1234, host='0.0.0.0')  # Run the app
