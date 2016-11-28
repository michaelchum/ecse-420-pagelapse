<?php

function signup_post()
{
	$error = false;
	$message = false;

	$email = $_POST['email'];
	
	if(isset($_POST['submit']))
	{
		if(filter_var($email, FILTER_VALIDATE_EMAIL) !== FALSE)
		{
			if(is_array($test))
				$error = "";
			else
			{
				// Add the email address to Mailchimp list and send out verification email.
				$mc = new MailChimp(MAILCHIMP_API_KEY);
				$result = $mc->call('lists/subscribe', array('id' => MAILCHIMP_LIST_ID, 
		  												     'email' => array('email' => $email),
		  												     'double_optin' => false,
		  												     'send_welcome' => true));
		  		
		  		// Adding to MC was successful, add to database and send success message
		  		if($result['email'] == $email)
					$message = "Welcome to McHacks! Stay tuned for more information.";
				else
					$error = "Error signing up occurred: " . $result['error'];
			}
		}
		else
		{
			$error = "That's not a valid email. A valid email looks something like helloworld@hackmcgill.com. Try again?";
		}
	}
	
	return array('message' => $message, 'error' => $error);
}

?>
