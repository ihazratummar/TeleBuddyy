from builtins import int
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from dotenv import load_dotenv
import os
import asyncio
from datetime import timedelta, datetime


load_dotenv()

API_NINJA_KEY = os.getenv("API_NINJA_KEY")
WEATHER_API = os.getenv("WEATHER_API")

class General:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["todo_collection"]

    async def quotes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            category = " ".join(context.args)
            print(category)
            api_url = f"https://api.api-ninjas.com/v1/quotes?category={category}"
            response = requests.get(api_url, headers={'X-Api-Key': f'{API_NINJA_KEY}'})
            if response.status_code == requests.codes.ok:
                quote_data = response.json()
                if quote_data:
                    quote = quote_data[0].get("quote", "No Quotes found")
                    author = quote_data[0].get("author", "Unknown")
                    formatted_message = f'"{quote}"\n\n- {author}'
                    await update.message.reply_text(formatted_message)
            else:
                print("Error: ", response.status_code, response.text)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        city_name = " ".join(context.args)
        if city_name:
            try:
                url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API}&q={city_name}&aqi=no"
                response = requests.get(url).json()
                location = response["location"]
                address = f'{location["name"]}, {location["region"]}, {location["country"]}'
                weather = response["current"]
                weather_condition = weather["condition"]

                await update.message.reply_markdown(
                    f"🏕️ Location: {address}\n\n🌡️Current Temp: {weather['temp_c']}°\nCondition: {weather_condition['text']}"
                )
            except Exception as e:
                print(f"Error: {e}")
        else:
            await update.message.reply_text("Enter city name")

    async def joke(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,racist,sexist,explicit"
        response = requests.get(url).json()

        if response:
            if response["type"] == "single":
                await update.message.reply_text(f"{response['category']}\n\n{response['joke']}")
            else:
                await update.message.reply_text(f"{response['category']}\n\n{response['setup']}")
                await asyncio.sleep(5)
                await update.message.reply_text(f"{response['delivery']}")
        else:
            await update.message.reply_text("No Joke Found")

    async def facts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        api_url = f"https://api.api-ninjas.com/v1/facts"
        response = requests.get(api_url, headers={'X-Api-Key': f'{API_NINJA_KEY}'})
        facts_data = response.json()
        if response.status_code == requests.codes.ok:
            facts = facts_data[0]
            print(facts)
            await update.message.reply_text(f"{facts['fact']}")

    async def remind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text("Usage: /remind [time in minutes] [message]")
                return

            time_in_minutes = int(args[0])
            remind_message = " ".join(args[1:])
            reminder_time = datetime.now() + timedelta(minutes=time_in_minutes)

            await update.message.reply_text(f"Reminder set for {time_in_minutes} minutes from now.")

            await asyncio.sleep(time_in_minutes * 60)
            await update.message.reply_text(f"Reminder: {remind_message}")
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    # Dictionary to store the counts of each option
    click_counts = {}
    # Dictionary to store users who have clicked
    user_clicks = {}

    async def poll(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            args = context.args
            if len(args) < 3:
                await update.message.reply_text("Usage: /poll [question] | [option1] | [option2] ...")
                return

            joined_args = ' '.join(args)
            parts = joined_args.split('|')

            if len(parts) < 3:
                await update.message.reply_text("Usage: /poll [question] | [option1] | [option2] ...")
                return

            question = parts[0].strip()
            options = [option.strip() for option in parts[1:]]

            # Initialize click counts for each option
            global click_counts, user_clicks
            click_counts = {option: 0 for option in options}
            user_clicks = {}

            keyboard = [[InlineKeyboardButton(option, callback_data=option)] for option in options]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(question, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"Error: {str(e)}")

    async def poll_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.from_user.id
        option = query.data

        # Check if the user has already clicked
        global user_clicks
        if user_id in user_clicks:
            await query.answer("You have already voted!", show_alert=True)
            return

        # Update the click count for the selected option
        global click_counts
        if option in click_counts:
            click_counts[option] += 1
            user_clicks[user_id] = option

        # Generate the updated message text with click counts
        result_text = "Selected option: {}\n\n".format(option)
        result_text += "\n".join([f"{opt}: {count}" for opt, count in click_counts.items()])

        # Recreate the keyboard to keep the buttons
        keyboard = [[InlineKeyboardButton(opt, callback_data=opt)] for opt in click_counts.keys()]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.answer()
        await query.edit_message_text(text=result_text, reply_markup=reply_markup)

    async def todo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.message.from_user.id)
        task_description = " ".join(context.args)

        if not task_description:
            await update.message.reply_text("Usage: /todo [task description]")
            return

        # First, update the document to initialize tasks array and task counter if it's a new document
        self.collection.update_one(
            {"_id": user_id},
            {
                "$setOnInsert": {
                    "name": update.message.from_user.full_name, 
                    "tasks": [],
                    "task_counter": 0  # Initialize task counter
                }
            },
            upsert=True
        )

        # Retrieve the current task counter and generate a new task ID
        user_data = self.collection.find_one({"_id": user_id})
        task_counter = user_data["task_counter"]
        task_id = task_counter + 1  # Sequential task ID

        # Increment the task counter for future tasks
        self.collection.update_one(
            {"_id": user_id},
            {
                "$inc": {"task_counter": 1}  # Increment the counter
            }
        )

        # Add the new task to the tasks array
        result = self.collection.update_one(
            {"_id": user_id},
            {
                "$push": {"tasks": {"task_id": task_id, "description": task_description, "completed": False}}
            }
        )

        if result.modified_count > 0 or result.upserted_id is not None:
            await update.message.reply_text("Todo Added\n\nTodo commands: \n/todo -To Todo \n/todo_list - Get the list of all Todo \n/complet_todo - To mark a todo complete \n/delete_todo -Get a single todo or All")
            await self.todo_list(update=update, context=context)
        else:
            await update.message.reply_text("Failed to add task.")

    async def todo_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.message.from_user.id)
        user_data = self.collection.find_one({"_id": user_id})
        
        if user_data:
            tasks = user_data.get("tasks", [])

            if tasks:
                task_list = "\n".join(
                    [f"<b>{task['task_id']}</b>. {task['description']} - Completed: <b>{'Yes' if task['completed'] else 'No'}</b>\n"
                    for task in tasks]
                )
                response_message = f"Your TODO List:\n\n{task_list}"
            else:
                response_message = "Your TODO list is currently empty."
        else:
            response_message = "You don't have any tasks yet. Add some with /todo command."

        # Send the response message to the user with HTML formatting
        await update.message.reply_text(response_message, parse_mode='HTML')

    async def complete_todo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.message.from_user.id)
        user_data = self.collection.find_one({"_id": user_id})

        args = context.args
        if len(args) < 2:
            await update.message.reply_text("Usage: /complete_todo [Task Number] [yes]")
            return
        

        task_number = int(args[0])
        is_complete = args[1].lower() == "yes"

        if user_data:
            tasks = user_data.get("tasks", [])
            if 0 < task_number <= len(tasks):
                task_id = tasks[task_number - 1]["task_id"]
                print(task_id)
                result = self.collection.update_one(
                    {"_id": user_id, "tasks.task_id": task_id},
                    {"$set":{"tasks.$.completed": is_complete}}
                ) 
                if result.modified_count > 0:
                    await update.message.reply_text("Task completed")
                    await self.todo_list(update=update, context=context)
                
                else:
                    await update.message.reply_text("Faield to compled the task")
            else:
                await update.message.reply_text("Invalid task number")
            
        else:
            await update.message.reply_text("No task found for you!")

    async def delete_todo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.message.from_user.id)
        user_data = self.collection.find_one({"_id": user_id})

        args = context.args
        if len(args) < 1:
            await update.message.reply_text("Usage: /delete_todo [Todo Number / all]")
            return
        
        if args[0].lower() == "all":
            if user_data and user_data.get("tasks", []):
                self.collection.update_one(
                    {"_id": user_id},
                    {"$set": {"tasks":[], "task_counter":0}}
                )
                await update.message.reply_text("All tasks have been deleted.")
            else:
                await update.message.reply_text("No task found to delete.")
        else:
            task_number = int(args[0])

            if user_data:
                tasks = user_data.get("tasks", [])
                if 0 < task_number <= len(tasks):
                    removed_task = tasks.pop(task_number - 1)

                    self.collection.update_one(
                        {"_id": user_id},
                        {"$set": {"tasks": tasks}, "$inc": {"task_counter": -1}}
                    )

                    for i, task in enumerate(tasks):
                        task["task_id"] = i + 1

                    self.collection.update_one(
                        {"_id": user_id},
                        {"$set": {"tasks": tasks}}
                    )
                    await update.message.reply_text(f"Deleted task {task_number}: {removed_task['description']}")
                    await self.todo_list(update=update, context=context)
                else:
                    await update.message.reply_text(f"Task number {task_number} does not exist.")   
            else:
                await update.message.reply_text("No task found")

