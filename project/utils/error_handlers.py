from flask import render_template


def register_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html', msg=error)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html', msg=error)

    @app.errorhandler(500)
    def bad_request(error):
        return render_template('500.html', msg=error)

    @app.errorhandler(502)
    def bad_request(error):
        return render_template('502.html', msg=error)
