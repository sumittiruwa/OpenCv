import cv2
user_image = input("Enter your image location=")
image_load = cv2.imread(user_image)

if image_load is None:
    print("Error:image Couldn't load")
else:
    gray = cv2.cvtColor(image_load,cv2.COLOR_BGR2GRAY)
    print("Select a choice:\n1.Show image \n2.Save image")
    choice = int(input("Enter your Choice:"))
    if choice ==1:
        print("Select a option:\n1.Colorful Image \n2.Grayscale Image")
        choice = int(input("Enter your choice="))
        if choice==1:
            cv2.imshow("Colorful Image",image_load)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        elif choice==2:
            cv2.imshow("Grayscale Image",gray)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            print("Invalid Choice: Please Check again")

    elif choice == 2:
        filename = input("Enter your filename=")
        print("Select choice:\n1.colorful \n2.Grayscale")
        choice = int(input("Enter Your Choice="))
        if choice==1:
            success = cv2.imwrite(filename,image_load)
        elif choice==2:
            success= cv2.imwrite(filename,gray)
        else:
            print("Invalid choice")
            success = False
        if success:
            print(f"filename saved Sucessfully {filename}")
        else:
            print("Filename didn't saved")