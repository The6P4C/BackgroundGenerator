from PIL import Image

def contrast(c1, c2):
	def relative_luminance(c):
		RsRGB = c[0] / 255
		GsRGB = c[1] / 255
		BsRGB = c[2] / 255

		R = ((RsRGB + 0.055) / 1.055) ** 2.4
		G = ((GsRGB + 0.055) / 1.055) ** 2.4
		B = ((BsRGB + 0.055) / 1.055) ** 2.4

		if RsRGB <= 0.03928:
			R = RsRGB / 12.92
		if GsRGB <= 0.03928:
			G = GsRGB / 12.92
		if BsRGB <= 0.03928:
			B = BsRGB / 12.92

		return 0.2126 * R + 0.7152 * G + 0.0722 * B

	l1 = relative_luminance(c1)
	l2 = relative_luminance(c2)

	return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

def distance_squared(c1, c2):
	r2 = (c1[0] - c2[0]) ** 2
	g2 = (c1[1] - c2[1]) ** 2
	b2 = (c1[2] - c2[2]) ** 2

	return r2 + g2 + b2

def find_contrast_pair(image, target):
	downsampled_image = image.resize((50, 50), Image.BICUBIC)

	width, height = downsampled_image.size
	image_data = downsampled_image.load()

	prev_contrast = -100
	color_pair = ((0, 0, 0), (0, 0, 0))

	for y1 in range(height - 1):
		for x1 in range(width - 1):
			for y2 in range(y1 + 1, height):
				for x2 in range(x1 + 1, width):
					c1 = image_data[x1, y1]
					c2 = image_data[x2, y2]

					cont = contrast(c1, c2)

					if abs(target - cont) < abs(target - prev_contrast):
						prev_contrast = cont
						color_pair = (c1, c2)

	return color_pair

def color_resample(image, colors):
	width, height = image.size
	image_data = image.load()

	new_image = Image.new('RGB', (width, height))
	new_image_data = new_image.load()

	for y in range(height):
		for x in range(width):
			c = image_data[x, y]

			distances = [(color, distance_squared(c, color)) for color in colors]
			closest_color = min(distances, key = lambda t: t[1])[0]

			new_image_data[x, y] = closest_color

	return new_image

def apply_effect(image, contrast_target):
	contrast_pair = find_contrast_pair(image, contrast_target)
	return color_resample(image, list(contrast_pair))
