import transmissionrpc
import Flask
from werkzeug import secure_filename


config = {}
with open('config.ini', 'r') as file:
    for line in file.read().splitlines():
        line = line.split('==')
        config[line[0]] = line[1]

app = Flask.Flask(__name__)  # Initialize our application
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024  # Set the upload limit to 1MiB
app.secret_key = config['SECRET_KEY']

tc = transmissionrpc.Client('localhost', port=9091)


def processNewTorrent(torrentfile):
    torrentID = tc.add_torrent(torrentfile)
    return torrentID

@app.route('/', methods=['GET', 'POST'])
def index():
    if Flask.request.method == 'POST':
        uploaded = Flask.request.files.getlist("file[]")
        for f in uploaded:
            if secure_filename(f.filename):
                f.save('static/torrents/%s' % secure_filename(f.filename))
                print 'Uploaded file "%s"' % secure_filename(f.filename)
                Flask.flash(Flask.Markup('Successfully uploaded torrent %s. Download starting...') % secure_filename(
                    f.filename))
            else:
                Flask.flash('Invalid filename.', Flask.url_for(index))

        return Flask.redirect(Flask.url_for('index'))  # Upload done, refresh.
    else:
        return Flask.render_template('index.html', torrents=tc.get_torrents())


if __name__ == '__main__':
    app.run()  # Run the app