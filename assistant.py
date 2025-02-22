import os
from openai import OpenAI
import json
from execute_sql import execute_sql
from dotenv import load_dotenv

load_dotenv()

print(os.getenv("OPENAI_API_KEY"))
print(os.getenv("HTTPS_PROXY"))
print(os.getenv("HTTP_PROXY"))

client = OpenAI()

tools = [
    {
      "type": "function",
      "function": {
        "name": "execute_sql",
        "description": "Executes an SQL query on a local SQLite database and returns the result as JSON.",
        "strict": False,
        "parameters": {
          "type": "object",
          "properties": {
            "query": {
              "type": "string",
              "description": "The SQL query to execute."
            }
          },
          "required": [
            "query"
          ]
        }
      }
    }
]

prompt ="""
Ты опытный знаток российский вин. 
Ты отвечаешь на вопросы пользователя, которые касаются российских вин. 
Есть база данных рейтинга вина с полями 'Регион', 'Производитель', 'Вино', 'Год', 'Рейтинг'. 
Имя таблицы  'wines'. 
Нужно преобразовать запрос пользователя в sql, вызвать функцию и преобразовать json в читаемый текст. 
Если вопрос пользователя не относится к данным этой базы, воспользуйся другими источниками. 
Вопросы на темы отличные от виноделия не отвечать. 
Тебе известны только вина из базы.
Тебя зовут Артур Саркисян
"""

question = "Как тебя зовут?"

model = "gpt-4o-mini"

messages=[{
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": prompt
        }
      ]
    },
]

def ask_assistant(question):
        
  if (question):
    messages.append({
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": question
          }
        ]
    })

  completion = client.chat.completions.create(
      model=model,
      messages=messages,
      tools=tools,
      temperature=1,
      max_completion_tokens=2048,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
  )

#  print(completion.choices[0].message.tool_calls)

  print(f'completion.usage.total_tokens: {completion.usage.total_tokens}')

  if not completion.choices[0].message.tool_calls:
    reply = completion.choices[0].message.content;
    messages.append({
        "role": "assistant",
        "content": [
          {
            "type": "text",
            "text": reply
          }
        ]
    })
    return reply

  tool_call = completion.choices[0].message.tool_calls[0]
  args = json.loads(tool_call.function.arguments)

  sql = args["query"]
  print(f'sql:{sql}')

  result = execute_sql(args["query"])


  messages.append(completion.choices[0].message)  # append model's function call message
  messages.append({                               # append result message
      "role": "tool",
      "tool_call_id": tool_call.id,
      "content": str(result)
  })

  completion_2 = client.chat.completions.create(
      model=model,
      messages=messages,
      tools=tools,
  )


  reply = completion_2.choices[0].message.content
  messages.append({
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": reply
        }
      ]
  })

  print(f'completion_2.usage.total_tokens: {completion_2.usage.total_tokens}')

  return reply

def main():
  while True:
    question = input("Ваш вопрос: ")
    reply = ask_assistant(question)     
    print(f'Ответ:\n {reply}')

if __name__ == "__main__":
    main()
