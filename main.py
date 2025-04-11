import os
import random
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# تفعيل التسجيل
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# مراحل المحادثة
COOKIE, ACC, SL = range(3)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'أهلا بك! سيتم اختيار كوكيز تلقائي.\n'
        'أرسل ايدي الحساب المستهدف:'
    )
    return ACC

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('❌ تم إلغاء العملية.')
    return ConversationHandler.END

def handle_acc(update: Update, context: CallbackContext) -> int:
    context.user_data['acc'] = update.message.text
    update.message.reply_text('كم عدد البلاغات اللي تحب تبعتها؟')
    return SL

def handle_sl(update: Update, context: CallbackContext) -> int:
    try:
        count = int(update.message.text)
        acc_id = context.user_data['acc']

        # اختيار كوكي عشوائي من الملف
        with open("coins.txt", "r") as f:
            coins = [line.strip() for line in f if line.strip()]
        if not coins:
            update.message.reply_text("⚠️ مفيش كوكيز متاحة حالياً.")
            return ConversationHandler.END

        c_user_id = random.choice(coins)
        cookie = f"c_user={c_user_id}; xs=FAKE_xs_token"  # عدل لو عندك xs حقيقي
        cookie_dict = {"c_user": c_user_id, "xs": "FAKE_xs_token"}

        update.message.reply_text("🚀 جاري إرسال البلاغات...")
        success = process_report(cookie_dict, acc_id, count)

        if success:
            update.message.reply_text(f"✅ تم إرسال {count} بلاغ بنجاح!")
        else:
            update.message.reply_text("❌ حصل خطأ أثناء التبليغ.")
    except ValueError:
        update.message.reply_text("⚠️ من فضلك أدخل رقم صحيح.")
        return SL
    finally:
        context.user_data.clear()

    return ConversationHandler.END

def process_report(cookies, acc_id, count):
    for i in range(count):
        try:
            # هنا منطق البلاغ - استبدله بالطلب اللي بتستخدمه
            logger.info(f"بلاغ رقم {i+1} على الحساب {acc_id} باستخدام {cookies['c_user']}")
        except Exception as e:
            logger.error(f"خطأ أثناء البلاغ: {str(e)}")
            return False
    return True

def main():
    TOKEN = os.getenv("7277046901:AAEZpktSUC_Q9PkcYShXaAGn4tuBojfIXuU")
    if not TOKEN:
        print("❌ BOT_TOKEN مش متعرف كمتغير بيئي!")
        return

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ACC: [MessageHandler(Filters.text & ~Filters.command, handle_acc)],
            SL: [MessageHandler(Filters.text & ~Filters.command, handle_sl)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
