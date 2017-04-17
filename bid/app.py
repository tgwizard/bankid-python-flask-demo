import logging
import sys

from flask import Flask, render_template, request, redirect, jsonify, session

from bid import bankid
from bid.bankid import UserCancelled


def create_app():
    configure_logging()

    app = Flask(__name__, )
    app.config['SECRET_KEY'] = 'test'

    configure_routes(app)
    return app


def configure_routes(app):
    @app.route('/')
    def index():
        context = {
            'status': session.get('status', 'unauthed'),
            'user_data': {},
        }
        if session.get('status') == 'signed_in':
            context['user_data'] = session.get('user_data')
        return render_template('index.html', **context)

    @app.route('/sign_out')
    def sign_out():
        session.clear()
        return redirect('/')

    @app.route('/api/authenticate', methods=['POST'])
    def authenticate():
        data = request.get_json()
        pid = data.get('pid')
        order_ref, auto_start_token = bankid.authenticate(pid)

        session['status'] = 'authenticating'
        session['order_ref'] = order_ref

        return jsonify({
            'auto_start_token': auto_start_token
        })

    @app.route('/api/auth_status', methods=['GET'])
    def get_auth_status():
        if session.get('status') == 'authenticating':
            try:
                status_data = bankid.get_status(session['order_ref'])
            except UserCancelled:
                session.clear()
                return jsonify({
                    'status': 'bankid_fault',
                    'message': 'User cancelled',
                })

            if status_data['progress_status'] == 'COMPLETE':
                logging.info('User auth complete')
                session['status'] = 'signed_in'
                session['user_data'] = status_data['user_info']
            else:
                return jsonify({
                    'status': 'authenticating'
                })

        if session.get('status') == 'signed_in':
            return jsonify({
                'status': 'signed_in',
                'user_data': session.get('user_data'),
            })

        return jsonify({
            'status': 'unauthed'
        })


def configure_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
