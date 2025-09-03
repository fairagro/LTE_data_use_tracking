from langchain.prompts import ChatPromptTemplate

prompt=ChatPromptTemplate.from_messages(
	[
		(
			"system",
            "Youa are an expert extraction algorithm. You will be given a scientific article. "
            "You only extract relevant information that is explicitly mentioned in the text. And nothing else. "
            "If you do not know the value of an attribute asked to extract, return null or empty list for the attribute. "
        )
    ]
)