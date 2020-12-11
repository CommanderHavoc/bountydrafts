import discord 
from discord.ext import commands
from discord.ext.commands import has_permissions
import json

client = commands.Bot(command_prefix=">")
token = 'Nzg0NTU1MDI5NDk1MTUyNjQw.X8q_zw.Jyg4MkF4jgh6799ttGX_DHYDzt0'
client.remove_command('help')

with open('storage.json', encoding='utf-8') as f:
  try:
    jobs = json.load(f)
  except ValueError:
    jobs = {}
    jobs['users'] = []

@client.command()
async def help(ctx):
    em = discord.Embed(
        title = "Help",
        color = discord.Color.dark_red()
    )
    em.add_field(name="addjob", value="Run this command to add a new job/bounty to the dashboard [>addjob | >aj]",inline=False)
    em.add_field(name="displayjobs", value="Run this command to display all jobs, even if they've been completed [>displayjobs | >dj]",inline=False)
    em.add_field(name="displayavailable", value="Run this command to display all jobs that haven't been done. [>displayavailable | >da]",inline=False)
    em.add_field(name="displayfinished", value="Run this command to display all jobs that have been done. [>displayfinished | >df]",inline=False)
    em.add_field(name="jobinfo", value="Run this command to only see a single job specified [>jobinfo <title of job> | >ji <title of job>]",inline=False)
    em.add_field(name="finishjob", value="Run this command to mark a job as finished [>finishjob <title of job> | >fj <title of job>]",inline=False)
    em.add_field(name="deletejob", value="Run this command to delete a job from the listing, its similar to >finishjob, but it entirely erases it from the database [>deletejob <title of job> | >delj <title of job>]",inline=False)
    em.add_field(name="revertfinishedjob", value="Run this command to unmark a job as finished [>revertfinishedjob <title of job> | >rfj]",inline=False)
    await ctx.send(embed = em)


@client.command(aliases=['aj'])
@commands.has_permissions(manage_nicknames = True)
async def addjob(ctx):
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    #Title
    em = discord.Embed(
        title = "What is the title of the job?",
        color = discord.Color.dark_gold()
    )
    em.set_footer(text="Type 'cancel' to cancel the command")
    await ctx.send(embed = em)
    
    title = str((await client.wait_for('message', check=check)).content)
    if title.lower() == "cancel":
        await ctx.send("Command Cancelled.")
        return
    
    #Description
    em2 = discord.Embed(
        title = "What is the description of the job?",
        color = discord.Color.dark_gold()
    )
    em2.set_footer(text="Type 'cancel' to cancel the command")
    await ctx.send(embed = em2)

    description = str((await client.wait_for('message', check=check)).content)
    if description.lower() == "cancel":
        await ctx.send("Command Cancelled.")
        return
    
    #Price
    em3 = discord.Embed(
        title = "What is the price of the job? (Must be at least 3,000,000 credits)",
        color = discord.Color.dark_gold()
    )
    em3.set_footer(text="Type 'cancel' to cancel the command")
    await ctx.send(embed = em3)

    price = str((await client.wait_for('message', check=check)).content)
    price = price.replace(',','')
    if price.lower() == "cancel":
        await ctx.send("Command Cancelled.")
        return
    elif int(price) < 3000000:
        await ctx.send("Price is too low, must be above 3,000,000 credits")
        await ctx.send("Command cancelled")
        return
    
    #Checking if its acceptable
    await ctx.send("```This is the job:```")
    em4 = discord.Embed(
        title = f"{title}",
        color = discord.Color.red()
    )
    em4.add_field(name = '**Description:**', value = f"{description}", inline=False)
    em4.add_field(name = '**Price:**', value = f"{price} credits", inline=False)
    em4.set_footer(text="Type 'cancel' to cancel adding this job to the job database. Type 'Go ahead' to add it to the database")
    await ctx.send(embed = em4)

    response = str((await client.wait_for('message', check=check)).content)

    if response.lower() == "cancel":
        await ctx.send("Job adding cancelled.")
        return
    if response.lower() == 'go ahead':
        for job in jobs['jobs']:
            if job['title'].lower() == title.lower():
                await ctx.send("Title is already in use, please choose another one")
                return
        jobs['jobs'].append({
            'title' : title,
            'description' : description,
            'price' : price,
            'availability' : 'available',
            'people' : 'None'
        })
        with open('storage.json','w+') as f:
            json.dump(jobs,f)
        await ctx.send("```Added to database```")
        return
    else:
        await ctx.send("Unknown Response, job adding still cancelled.")



@client.command(aliases=['dj'])
async def displayjobs(ctx):
    em = discord.Embed(
        title = "All Jobs",
        color = discord.Color.blue()
    )
    for job in jobs['jobs']:
        if job['availability'] != 'deleted':
            em.add_field(name=f" <:credits:647021662662819850> {job['price']} - {job['title']} - {job['availability']}", value = job['description'], inline=False)
    await ctx.send(embed = em)

@client.command(aliases=['da'])
async def displayavailable(ctx):
    em = discord.Embed(
        title = f"Available Jobs",
        color = discord.Color.blue()
    )
    for job in jobs['jobs']:
        if job['availability'] == 'available':
            em.add_field(name=f" <:credits:647021662662819850> {job['price']} - {job['title']}", value = job['description'], inline=False)
    await ctx.send(embed = em)

@client.command(aliases=['df'])
async def displayfinished(ctx):
    em = discord.Embed(
        title = f"Finished Jobs",
        color = discord.Color.blue()
    )
    for job in jobs['jobs']:
        if job['availability'] == 'not available':
            em.add_field(name=f" <:credits:647021662662819850> {job['price']} - {job['title']}", value = job['description'], inline=False)
    await ctx.send(embed = em)


@client.command(aliases=['ji'])
async def jobinfo(ctx, *,jobname):
    for job in jobs['jobs']:
        if jobname.lower() == job['title'].lower():
            em = discord.Embed(
                title = f"Job Title: {job['title']}",
                color = discord.Color.blue()
            )
            em.add_field(name="Description:", value = job['description'], inline=False)
            em.add_field(name = "Price:", value = f"{job['price']} <:credits:647021662662819850>", inline=False)
            em.add_field(name= "Availability:", value = f"{job['availability']}", inline=False)
            em.add_field(name="People who've done the job:", value="** **")
            for userid in job['people']:
                em.add_field(name="** **", value=f"<@{userid}>", inline = False)
            await ctx.send(embed = em)  
            return

    await ctx.send("```Sorry, can't find the job you were looking for. Try checking your spelling, or do .displayjobs```") 
    return



@client.command(aliases=['fj'])
@commands.has_permissions(manage_nicknames = True)
async def finishjob(ctx,*,person):
    removeChar = ["<@!",">"]
    personlist = person.split()
    newpsnlst = []
    for userid in personlist:
        for word in removeChar:
            userid = userid.replace(word,'')
        newpsnlst.append(int(userid))
    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel
    em = discord.Embed(
        title = "What is the name of the job?",
        color = discord.Color.dark_blue()
    )
    em.set_footer(text = "Type cancel to cancel")
    await ctx.send(embed = em)
    jobname = str((await client.wait_for('message', check=check)).content)
    if jobname == 'cancel':
        return
    for job in jobs['jobs']:
        if jobname.lower() == job['title'].lower():
            job['availability'] = 'not available'
            job['people'] = newpsnlst
            with open('storage.json', 'w+') as f:
                json.dump(jobs,f)
            await ctx.send("```Job availablity updated```")
            return
    await ctx.send("```Job not found. Check the spelling of the job title```")
    return


@client.command(aliases=['rfj'])
@commands.has_permissions(manage_nicknames = True)
async def revertfinishedjob(ctx,*,jobname):
    for job in jobs['jobs']:
        if jobname.lower() == job['title'].lower():
            if job['availability'] == 'not available':
                job['availability'] = 'available'
                with open('storage.json', 'w+') as f:
                    json.dump(jobs,f)
                await ctx.send("```Job availablity updated```")
                return
            else:
                await ctx.send("```Job is already available```")
    await ctx.send("```Job not found. Check the spelling of the job title```")
    return

@client.command(aliases=['delj'])
@commands.has_permissions(manage_nicknames = True)
async def deletejob(ctx,*,jobname):
    for job in jobs['jobs']:
        if jobname.lower() == job['title'].lower():
            job['availability'] = 'deleted'
    with open('storage.json', 'w+') as f:
                    json.dump(jobs,f)

@client.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.MissingPermissions):
        await ctx.send("You're missing permissions to execute that command!")
    elif isinstance(error,commands.MissingRequiredArgument):
        await ctx.send("Please enter all the required arguements!")


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=">help | Developed by Impact#1704"))
    print("Bot is online")

client.run(token)
