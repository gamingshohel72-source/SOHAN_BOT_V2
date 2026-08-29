ROUTES = {}


def route(name):

    def wrapper(func):

        ROUTES[name] = func

        return func

    return wrapper

async def open_page(update, context, data):

    # Exact Route আগে
    if data in ROUTES:

        print("EXACT:", data)

        await ROUTES[data](update, context)

        return True

    # Prefix Route (Longest First)
    prefixes = sorted(

        ROUTES.keys(),

        key=len,

        reverse=True

    )

    for prefix in prefixes:

        if data.startswith(prefix + "_"):

            print("MATCH:", prefix)

            await ROUTES[prefix](update, context)

            return True

        # Route নিজেই _ দিয়ে শেষ হলে
        if prefix.endswith("_") and data.startswith(prefix):

            print("MATCH:", prefix)

            await ROUTES[prefix](update, context)

            return True

    print("NO ROUTE:", data)

    return False
