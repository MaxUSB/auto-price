from modules import Parser


def run():
    parser = Parser(
        url='https://auto.ru/-/ajax/desktop/listing/',
        out_dir='data',
        start_price=100000,
        stop_price=1000000
    )
    parser.get_cars()


if __name__ == '__main__':
    run()
