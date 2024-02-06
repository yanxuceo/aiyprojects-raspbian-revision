from button_class import Button

def main():
    # Create a Button instance (replace 'D17' with your actual GPIO pin)
    button = Button('D17')

    while True:
        button.wait_for_press()
        print('ON', flush = True)
        button.wait_for_release()
        print('OFF', flush = True)

    # Don't forget to close the button when done
    button.close()

if __name__ == '__main__':
    main()
