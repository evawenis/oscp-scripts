from urllib.parse import unquote_plus as urldec
import sys

def print_verbose(payload, left, right):
    print(
        f"debug: {urldec(left + payload + right)}", file=sys.stderr)


def print_data(databases, tables, columns, data):
    for db in databases:
        for tb in tables[db]:
            print()
            print(f"SELECT * FROM {db}..{tb};")
            print('\t'.join(columns[db][tb]))
            leng = max([len(data[db][tb][cl]) for cl in columns[db][tb]])

            for i in range(leng):
                result = []
                for cl in columns[db][tb]:
                    try:
                        result.append(data[db][tb][cl][i])
                    except KeyboardInterrupt:
                        exit(1)
                    except:
                        result.append('')

                print('\t'.join(result))

    print()
