

class User():
	def __init__(self, username, client_id, color):
		self.username = username
		self.client_id = client_id
		self.color = color

		self.is_authenticated = False
		self.is_active = True
		self.is_anonymous = False

	def get_id():
		return client_id
