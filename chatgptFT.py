from CoreLLM import *
if __name__ == "__main__":
    results=None
    while True:
        natural_language_query = input("Enter your query: ")
        try:
            if results is not None:
                results=query_llm("summarise "+ str(results))
                print("\n\n\nOutput Summary....\n\n",results)
                continue
            else:
                results = get_results_from_natural_language_query(natural_language_query)
                if len(results)>20:
                    results=results[0:19]
            for result in results:
                print(result)
        except Exception as e:
            print(f"An error occurred: {e}")	