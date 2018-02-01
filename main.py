import logging
import os
from PIL import Image
import praw
import tempfile
import two_color_effect
import urllib.request

import config

logging.basicConfig(format='|%(levelname)s| %(message)s', level=logging.DEBUG)

def get_url_extension(url):
	return url.split('.')[-1]

def is_image_url(url):
	extension = get_url_extension(url)
	return extension in ['jpg', 'jpeg', 'png', 'bmp']

def main():
	reddit = praw.Reddit(
		client_id=config.REDDIT_CLIENT_ID,
		client_secret=config.REDDIT_CLIENT_SECRET,
		user_agent='windows_python:BackgroundGenerator:v1.0.0 (by /u/The6P4C)'
	)

	images = []
	for submission in reddit.subreddit(config.SUBREDDIT).top(config.TOP_TIME, limit=10):
		logging.info(f'Checking submission {submission}')

		if not is_image_url(submission.url):
			logging.info('Submission was not an image.')
			continue

		extension = get_url_extension(submission.url)
		suffix = f'.{extension}'
		download_file_path = tempfile.mkstemp(suffix=suffix)[1]

		logging.info(f'Downloading image to {download_file_path}')

		urllib.request.urlretrieve(submission.url, download_file_path)

		image = None
		try:
			image = Image.open(download_file_path)

			if image.size != (1920, 1080):
				logging.info('Image size was invalid.')
				continue
		except:
			logging.info('Image was invalid.')
			continue

		images.append(image)

		if len(images) == 2:
			break

	processed_images = []
	for i, image in enumerate(images):
		logging.info(f'Processing image {i}.')

		processed_images.append(
			two_color_effect.apply_effect(image, config.CONTRAST_TARGET)
		)

		logging.info('Finished processing.')

	output = Image.new('RGB', (1920 * 2, 1080))
	for i, image in enumerate(processed_images):
		output.paste(image, (1920 * i, 0))

	output.save('out.png', 'PNG')

	logging.info('Saved stitched image.')

	logging.info('Refreshing background...')

	os.system('WallpaperChanger.exe out.png 3')

if __name__ == '__main__':
	main()
