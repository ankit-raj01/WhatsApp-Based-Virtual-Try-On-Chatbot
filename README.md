# WhatsApp Based Virtual Try-On Chatbot

https://github.com/user-attachments/assets/5f1757f0-4cef-4c5c-a169-c093993d5c46

This project showcases an innovative solution that integrates machine learning and messaging technologies, deployed on Render for scalability and reliability. By combining a Hugging Face space model with Twilio’s API for WhatsApp, the system allows users to visualize themselves in desired garments through an intuitive chatbot interface. This application demonstrates the potential of AI-driven tools in revolutionizing user experiences, particularly in fashion and e-commerce.

The process begins with user interaction on WhatsApp, where a chatbot powered by Twilio facilitates step-by-step guidance. Users are prompted to upload an image of themselves, followed by an image of the garment they wish to try on. Once both images are uploaded, they are processed by a pre-trained Hugging Face model hosted on Gradio. This model generates a photorealistic composite image of the user wearing the selected outfit, showcasing the advanced capabilities of virtual try-on technology. The resulting image is then uploaded to Google Drive using the Google API, with public sharing enabled via a unique link. The final step involves the chatbot, using Twilio’s API, to deliver this image back to the user on WhatsApp, completing the interaction and providing a polished, professional result.

The solution leverages Flask as the backend framework to handle communication between APIs, ensuring efficient and reliable operations. Render serves as the deployment platform, offering a scalable and robust environment for hosting the application. The Hugging Face model produces high-quality visual results, while Google Drive integration provides secure and convenient image sharing.

By bridging the gap between physical and digital experiences, this virtual try-on solution offers significant value in online retail and personalized styling. Its deployment on Render ensures a scalable, production-ready implementation.
