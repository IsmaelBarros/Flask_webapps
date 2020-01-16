from flask import Flask, render_template, request, session, copy_current_request_context
from vsearch import search4letters
from webapp.database_cm.DBcm import UseDataBase, ConnectionError, CredentialsError, SqlError
from webapp.checker.checker import check_logged_in
from threading import Thread

app = Flask(__name__)

app.secret_key = '123456'

app.config['dbconfig'] = {'host': '127.0.0.1',
                'user': 'vsearch',
                'password': 'vsearchpasswd',
                'database': 'vsearchlogdb',
                }

def log_request(req: 'flask_request', res: str) -> None:
    """Log details of web request and the results"""

    with UseDataBase(app.config['dbconfig']) as cursor:

        _SQL = """insert into log
            (phrase, letters, ip, browser_string, results)
            values
            (%s, %s, %s, %s, %s)"""

        cursor.execute(_SQL, (req.form['phrase'],
                          req.form['letters'],
                          req.remote_addr,
                          req.user_agent.browser,
                          res,))


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    """Extract the posted data, perform the search, return results """

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """Log details of web request and the results"""

        with UseDataBase(app.config['dbconfig']) as cursor:
            _SQL = """insert into log
                (phrase, letters, ip, browser_string, results)
                values
                (%s, %s, %s, %s, %s)"""

            cursor.execute(_SQL, (req.form['phrase'],
                                  req.form['letters'],
                                  req.remote_addr,
                                  req.user_agent.browser,
                                  res,))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = 'Aqui estão seus resultados:'
    results = str(search4letters(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
        return render_template('results.html',
                               the_title=title,
                               the_phrase=phrase,
                               the_letters=letters,
                               the_results=results,)
    except ConnectionError as err:
        print('Seu bando de dados está disponivel? Error: ', str(err))
    except CredentialsError as err:
        print('Problema com usuário ou senha . Error: ', str(err))
    except SqlError as err:
        print('Sua busca está correta? Error:', str(err))
    except Exception as err:
        print('Alguma coisa deu errado: ', str(err))
    return 'Error'


@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Bem vindo ao buscador de letras na web!')


@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML table"""

    with UseDataBase(app.config['dbconfig']) as cursor:
        _SQL = """select phrase, letters, ip, browser_string, results from log"""
        cursor.execute(_SQL)
        contents = cursor.fetchall()

    titles = ('Phrase', 'Letters', 'Remote_addr', 'User_agent', 'Results')
    return render_template('viewlog.html',
                           the_title='View Log',
                           the_row_titles=titles,
                           the_data=contents,
                           )


@app.route('/login')
def do_login() -> str:
    session['loggedin'] =True
    return 'Você está logado'


@app.route('/logout')
def do_logout() -> str:
    session.pop('loggedin')
    return 'Você fez o logged out'


if __name__ == '__main__':
    app.run(debug=True)
