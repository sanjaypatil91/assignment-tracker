

create table user(
				user_id int AUTO_INCREMENT,
				name varchar (50),
				email varchar (50),	
				password varchar (50),
				type_of_user varchar (50),
                primary key (user_id)

);

create table assignment(
				assignment_id int,
				assignment_title varchar (100),
				description varchar (1000),
				submission_due_date varchar (30),
				primary key(assignment_id)
);				

create table submission(
				submission_id int,
				assignment_id int,	
				user_id int,
				submission_date varchar (30),
				solution  varchar (1000),
				status_of_assignment varchar (30),
				foreign key (assignment_id) references assignment(assignment_id),
				foreign key (user_id) references user(user_id)
			
);				












































