import openai

openai.api_key = "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"

model_engine = "text-davinci-002"
prompt = "Hi, how are you doing today?"

completions = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.7,
)

message = completions.choices[0].text
print(message)